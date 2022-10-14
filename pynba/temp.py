from dataclasses import dataclass
from collections.abc import Callable

import pandas as pd
import numpy as np
from scipy import sparse, stats


POSS_COLS = [
    "off_player0",
    "off_player1",
    "off_player2",
    "off_player3",
    "off_player4",
    "def_player0",
    "def_player1",
    "def_player2",
    "def_player3",
    "def_player4",
    "points_scored",
    "possession_num",
    "date",
]
EPOCH = pd.Timestamp("1970-01-01")
nba_player_ids = pd.read_csv(
    "/root/nba/data/NBA_Player_IDs.csv", encoding_errors="ignore"
)
player_id_mapping = {
    int(player_id): player_name
    for player_name, player_id in zip(
        nba_player_ids["NBAName"], nba_player_ids["NBAID"]
    )
    if not pd.isna(player_id)
}


@dataclass(frozen=True)
class SparseWeightedRidgeRegression:
    """
    Weighted ridge regression using SciPy sparse matrices

    y = X * k + errors
    V(y|X) = V(errors) = 1 / w (actually a matrix with this as its diagonal)
    V(k) = k_prior_var (actually a matrix with this as its diagonal),
    where k_prior_var is normalized to V(y|X), i.e. w.

    Each observation (row of X) is weighted by w, i.e. weighted least squares.

    XT_W = X^T * W, where W is the matrix with w as its diagonal
    G = 1 / k_prior_var (actually a matrix with this as its diagonal)
    A = X^T * W * X + G
    b = X^T * W * y
    k_hat = A^-1 * b (we actually solve for this instead of calculating the inverse
    for computational reasons, but you get the idea)

    k_hat minimizes (y - X * k_hat)^T * W * (y - X * k_hat) + k_hat^T * G * k_hat

    k_hat_cov = V(k_hat)
    """

    X: sparse.csr_matrix
    y: np.array
    w: np.array
    k_prior_var: np.array
    XT_W: sparse.csr_matrix
    G: sparse.dia_matrix
    A: sparse.csr_matrix
    b: np.array
    k_hat: np.array

    @classmethod
    def fit(
        cls, X: sparse.csr_matrix, y: np.array, w: np.array, k_prior_var: np.array
    ) -> None:
        XT_W = X.multiply(w).T.tocsr()
        G = sparse.diags(1 / k_prior_var)
        A = XT_W.dot(X) + G
        b = XT_W.dot(y)
        k_hat = sparse.linalg.spsolve(A, b)
        return cls(X, y, w, k_prior_var, XT_W, G, A, b, k_hat)

    def predict(self, X: sparse.csr_matrix) -> np.array:
        return X.dot(self.k_hat)

    def score(self, X: sparse.csr_matrix, y: np.array) -> float:
        y_hat = self.predict(X)
        error = y - y_hat
        return stats.norm.logpdf(error).sum()

    @property
    def k_hat_cov(self) -> np.array:
        """Calculate this lazily since inverting A is expensive"""
        residuals = self.y - self.predict(self.X)
        degrees_of_freedom = self.X.shape[0] - self.X.shape[1]
        est_err_var = (residuals * self.w).dot(residuals) / degrees_of_freedom
        return est_err_var * sparse.linalg.inv(self.A.tocsc())


@dataclass(frozen=True)
class _RAPMData:
    X: sparse.csr_matrix
    y: np.array
    y_var: np.array
    time: np.array
    player_ids: np.array

    @classmethod
    def from_possessions(cls, poss: pd.DataFrame) -> "_RAPMData":
        stints = cls._calc_stints(poss)
        y, y_var = cls._calc_y_y_var(poss, stints)
        time = cls._calc_time(stints)
        player_ids = cls._calc_player_ids(stints)
        X = cls._calc_X(stints, player_ids, player_ids.shape[0])
        return cls(X, y, y_var, time, player_ids)

    def __getitem__(self, index) -> "_RAPMData":
        cls = type(self)
        return cls(
            self.X[index],
            self.y[index],
            self.y_var[index],
            self.time[index],
            self.player_ids,
        )

    @classmethod
    def _calc_stints(cls, poss: pd.DataFrame) -> pd.DataFrame:
        poss = poss.loc[:, POSS_COLS]
        off_player_ids = poss[[f"off_player{ind}" for ind in range(5)]].to_numpy()
        off_player_ids.sort(1)
        poss["off_player_ids"] = [row.tobytes() for row in off_player_ids]
        def_player_ids = poss[[f"def_player{ind}" for ind in range(5)]].to_numpy()
        def_player_ids.sort(1)
        poss["def_player_ids"] = [row.tobytes() for row in def_player_ids]
        stints = (
            poss.groupby(by=["date", "off_player_ids", "def_player_ids"])
            .agg(
                {
                    "off_player0": "first",
                    "off_player1": "first",
                    "off_player2": "first",
                    "off_player3": "first",
                    "off_player4": "first",
                    "def_player0": "first",
                    "def_player1": "first",
                    "def_player2": "first",
                    "def_player3": "first",
                    "def_player4": "first",
                    "points_scored": "sum",
                    "possession_num": "count",
                }
            )
            .reset_index()
        )
        stints["days_since_epoch"] = cls._calc_days_since_epoch(stints["date"])
        stints.sort_values("date", inplace=True)
        del stints["off_player_ids"], stints["def_player_ids"]
        return stints.reset_index(drop=True)

    @staticmethod
    def _calc_days_since_epoch(dates: pd.Series) -> np.array:
        dates = pd.DatetimeIndex(dates)
        return (dates - EPOCH).days.to_numpy().astype(float)

    @classmethod
    def _calc_y_y_var(
        cls, poss: pd.DataFrame, stints: pd.DataFrame
    ) -> tuple[np.array, np.array]:
        alpha = np.exp(np.log(0.5) / 20)
        alpha_4 = np.exp(np.log(0.5) / 100)
        points_df = (
            poss.groupby(["points_scored", "date"])
            .agg(count=("off_team_id", "count"))
            .reset_index()
        )
        points_df["days_since_epoch"] = cls._calc_days_since_epoch(points_df["date"])
        days = points_df["days_since_epoch"].unique()
        points = [1, 2, 3]
        df_dict = {point: [] for point in points + [4]}

        filts = {point: points_df["points_scored"] == point for point in points + [4]}

        for day in days:
            weights = (
                alpha ** np.abs(points_df["days_since_epoch"] - day)
            ) * points_df["count"]
            divisor = weights.sum()
            for point in points:
                est = weights[filts[point]].sum() / divisor
                df_dict[point].append(est)

        for day in days:
            weights = (
                alpha_4 ** np.abs(points_df["days_since_epoch"] - day)
            ) * points_df["count"]
            divisor = weights.sum()
            est = weights[filts[4]].sum() / divisor
            df_dict[4].append(est)

        df = pd.DataFrame(df_dict, index=days)
        unique_pts = points_df["points_scored"].unique()
        other_pts = unique_pts[unique_pts > 4]
        for point in other_pts:
            df[point] = (
                points_df.loc[points_df["points_scored"] == point, "count"].sum()
                / points_df["count"].sum()
            )

        df["mu"] = sum([df[point] * point * 100 for point in unique_pts])
        df["var"] = (
            sum([df[point] * (point * 100) ** 2 for point in unique_pts])
            - df["mu"] ** 2
        )
        mu = stints["days_since_epoch"].map(df["mu"])
        y_var = (
            stints["days_since_epoch"].map(df["var"]) / stints["possession_num"]
        ).to_numpy()
        y = (stints["points_scored"] / stints["possession_num"] * 100 - mu).to_numpy()
        return y, y_var

    @staticmethod
    def _calc_time(stints: pd.DataFrame) -> np.array:
        return stints["days_since_epoch"].to_numpy().astype(float)

    @staticmethod
    def _calc_player_ids(stints: pd.DataFrame) -> np.array:
        cols = [f"off_player{ind}" for ind in range(5)] + [
            f"def_player{ind}" for ind in range(5)
        ]
        return np.unique(stints.loc[:, cols])

    @staticmethod
    def _calc_X(
        stints: pd.DataFrame, player_ids: np.array, n_players: int
    ) -> sparse.csr_matrix:
        off_player_ids = stints.loc[
            :, [f"off_player{ind}" for ind in range(5)]
        ].to_numpy()
        def_player_ids = stints.loc[
            :, [f"def_player{ind}" for ind in range(5)]
        ].to_numpy()
        n_stints = stints.shape[0]

        X = sparse.lil_matrix((2 * n_players, n_stints))
        for ind, player_id in enumerate(player_ids):
            X[ind, :] = (player_id == off_player_ids).any(1)
            X[n_players + ind, :] = (player_id == def_player_ids).any(1)

        return X.T.tocsr().astype("float64")

    @property
    def n_players(self) -> int:
        return self.player_ids.shape[0]


@dataclass(frozen=True)
class TimeDecayedRAPM:
    """
    Time-decayed, regularized, adjusted plus-minus with differing priors.
    """

    data: _RAPMData
    model: SparseWeightedRidgeRegression
    date: int
    half_life: float
    off_prior: float
    def_prior: float

    @classmethod
    def from_possessions(
        cls,
        poss: pd.DataFrame,
        date: int,
        half_life: float,
        off_prior: float,
        def_prior: float,
    ) -> None:
        """Alternative constructor using a pd.DataFrame of possessions"""
        data = _RAPMData.from_possessions(poss)
        return cls.from_data(data, date, half_life, off_prior, def_prior)

    @classmethod
    def from_data(
        cls,
        data: _RAPMData,
        date: int,
        half_life: float,
        off_prior: float,
        def_prior: float,
    ) -> None:
        """Alternative constructor using a pre-calculate _RAPMData object"""
        k_prior_var = np.array(
            [off_prior**2] * data.n_players + [def_prior**2] * data.n_players
        ).astype(float)
        rel_time = data.time - date
        w = np.exp(np.log(0.5) / half_life) ** np.abs(rel_time) / data.y_var
        model = SparseWeightedRidgeRegression.fit(data.X, data.y, w, k_prior_var)
        return cls(data, model, date, half_life, off_prior, def_prior)

    @property
    def stats(self) -> pd.DataFrame:
        """Stats table for time-decayed RAPM"""
        rapm, off_rapm, def_rapm = self._rapm
        rapm_std, off_rapm_std, def_rapm_std = self._stds
        off_poss, def_poss, raw_pm, off_raw_pm, def_raw_pm = self._raw_stats
        return pd.DataFrame(
            {
                "name": self._names,
                "rapm": rapm,
                "off_rapm": off_rapm,
                "def_rapm": def_rapm,
                "rapm_std": rapm_std,
                "off_rapm_std": off_rapm_std,
                "def_rapm_std": def_rapm_std,
                "off_poss": off_poss,
                "def_poss": def_poss,
                "raw_pm": raw_pm,
                "off_raw_pm": off_raw_pm,
                "def_raw_pm": def_raw_pm,
            },
            index=self.data.player_ids,
        )

    @property
    def _rapm(self) -> tuple[np.array, np.array, np.array]:
        k_hat = self.model.k_hat
        n_players = self.data.n_players

        off_rapm, def_rapm = k_hat[:n_players], -k_hat[n_players:]
        rapm = off_rapm + def_rapm
        return rapm, off_rapm, def_rapm

    @property
    def _stds(self) -> tuple[np.array, np.array, np.array]:
        k_hat_cov = self.model.k_hat_cov
        n_players = self.data.n_players

        x_var = k_hat_cov.diagonal()
        off_def_cov = k_hat_cov.diagonal(n_players)
        off_rapm_var, def_rapm_var = x_var[:n_players], x_var[n_players:]
        rapm_var = off_rapm_var + def_rapm_var + 2 * off_def_cov
        return np.sqrt(rapm_var), np.sqrt(off_rapm_var), np.sqrt(def_rapm_var)

    @property
    def _raw_stats(self) -> tuple[np.array, np.array, np.array, np.array, np.array]:
        XT_W = self.model.XT_W
        n_players = self.data.n_players
        b = self.model.b

        poss = np.asarray(XT_W.sum(1)).reshape(-1)
        off_poss, def_poss = (
            poss[:n_players] * self._curr_var,
            poss[n_players:] * self._curr_var,
        )
        raw_pms = b / poss
        off_raw_pm, def_raw_pm = raw_pms[:n_players], -raw_pms[n_players:]
        raw_pm = off_raw_pm + def_raw_pm
        return off_poss, def_poss, raw_pm, off_raw_pm, def_raw_pm

    @property
    def _curr_var(self) -> float:
        """Interpolate the current V(y|X), no extrapolation. Could be better..."""
        date = self.date
        time = self.data.time
        y_var = self.data.y_var

        xp, index = np.unique(time, return_index=True)
        yp = y_var[index]
        return np.interp(date, xp, yp)

    @property
    def _names(self) -> list[str]:
        player_ids = self.data.player_ids

        return [player_id_mapping.get(player_id, "n/a") for player_id in player_ids]


def optimize(
    poss: pd.DataFrame,
    half_life_range: tuple[float, float],
    off_prior_range: tuple[float, float],
    def_prior_range: tuple[float, float],
    rounds: int,
    frac: float = 0.5,
    time_step: float = 1,
) -> None:
    data = _RAPMData.from_possessions(poss)
    start_time = data.time.min() + frac * (data.time.max() - data.time.min())

    def score(half_life: float, off_prior: float, def_prior: float) -> float:
        log_likelihood = 0
        for date, train_index, test_index in ts_cv(data.time, start_time, time_step):
            train_data = data[train_index]
            time_decayed_rapm = TimeDecayedRAPM.from_data(
                train_data, date, half_life, off_prior, def_prior
            )
            X_test = data.X[test_index]
            y_test = data.y[test_index]
            log_likelihood += time_decayed_rapm.model.score(X_test, y_test)
        return log_likelihood

    return pattern_search(
        score, rounds, half_life_range, off_prior_range, def_prior_range
    )


def pattern_search(
    func: Callable, rounds: int, *args: tuple[float, float]
) -> tuple[tuple[float, ...], float, np.array, list[tuple[tuple[float, ...], float]]]:
    """
    Pattern search maximizes the callable func using a kind of binary search
    that halves the search space with 1.5 evaluations of the function. This
    assumes that func is concave (since we're maximizing).

    Args:
        func:
            callable to be optimized
        rounds:
            number of halvings for each dimension to perform
        *args:
            each additional argument defines the search space, i.e. the minimum
            and maximum for that dimension

    Returns:
        - The tuple of inputs that maximizes func.
        - The output of func for that input.
        - The bounds within which the true maximum resides.
        - The history of inputs and outputs evaluated during the search.
    """
    bounds = np.array([[arg[0], arg[1]] for arg in args]).astype(float)
    x1 = bounds.mean(1)
    y1 = func(*x1)
    steps = np.diff(bounds, 1).reshape(-1) / 4
    history = [(tuple(x1), y1)]
    for _ in range(rounds):
        for ind, step in enumerate(steps):
            x0 = x1.copy()
            x0[ind] -= step
            y0 = func(*x0)
            history.append((tuple(x0), y0))
            if y0 > y1:
                bounds[ind, 1] = x1[ind]
                x1, y1 = x0, y0
                continue
            x2 = x1.copy()
            x2[ind] += step
            y2 = func(*x2)
            history.append((tuple(x2), y2))
            if y2 > y1:
                bounds[ind, 0] = x1[ind]
                x1, y1 = x2, y2
            else:
                bounds[ind, 0] = x0[ind]
                bounds[ind, 1] = x2[ind]
        steps /= 2
    return tuple(x1), y1, bounds, history


def ts_cv(time: np.array, start_time: float, time_step: float):
    """
    Time series cross-validation, a generator for producing
    train and test indexes. Time does not need to be
    monotonically increasing.
    """
    index = np.arange(time.shape[0])
    unique_times = np.sort(np.unique(time))
    start_time = unique_times[unique_times >= start_time][0]
    while True:
        stop_time = start_time + time_step
        train_index = index[time < start_time]
        test_index = index[(time >= start_time) & (time < stop_time)]
        yield start_time, train_index, test_index

        filt = unique_times >= stop_time
        if not filt.any():
            break
        start_time = unique_times[filt][0]
