"""Model team statistics"""

import pandas as pd
import pymc3 as pm

from pynba import plot_logos, team_id_to_team_abb
from pynba.load_parsed_data import (
    estimate_shot_rate,
    estimate_attempt_rate,
    calc_scoring_rate,
)


DEFAULT_PRIORS = {
    "off_three_make_rate_sigma": 0.02,
    "off_two_make_rate_sigma": 0.02,
    "off_three_attempt_rate_sigma": 0.05,
    "off_off_reb_rate_sigma": 0.02,
    "off_turnover_rate_sigma": 0.01,
    "off_ft_attempt_rate_sigma": 0.02,
    "off_pace_sigma": 0.5,
    "off_ft_make_rate_sigma": 0.03,
    "def_three_make_rate_sigma": 0.01,
    "def_two_make_rate_sigma": 0.02,
    "def_three_attempt_rate_sigma": 0.02,
    "def_off_reb_rate_sigma": 0.02,
    "def_turnover_rate_sigma": 0.01,
    "def_ft_attempt_rate_sigma": 0.02,
    "def_pace_sigma": 0.25,
    "home_three_make_rate_diff": 0.0035,
    "home_three_make_rate_sigma": 0.001,
    "home_two_make_rate_diff": 0.0065,
    "home_two_make_rate_sigma": 0.002,
    "home_off_reb_rate_diff": 0.05,
    "home_off_reb_rate_sigma": 0.002,
    "home_turnover_rate_diff": -0.0002,
    "home_turnover_rate_sigma": 0.0001,
    "home_ft_attempt_rate_diff": 0.005,
    "home_ft_attempt_rate_sigma": 0.002,
    "home_ft_make_rate_diff": 0.001,
    "home_ft_make_rate_sigma": 0.0005,
    "sigma_ft_attempt_rate_mu": 0.05,
    "sigma_ft_attempt_rate_sigma": 0.01,
    "sigma_pace_mu": 0.08,
    "sigma_pace_sigma": 0.01,
}


class TeamsModel:
    """Class wrapper for teams PyMC3 model"""

    def __init__(self, games, priors=None):
        self.priors = self._process_priors(priors)
        self._assign_games(games)
        self._assign_model()

    @staticmethod
    def _process_priors(priors):
        default_priors = DEFAULT_PRIORS.copy()
        if priors is not None:
            for key in priors:
                if key not in default_priors:
                    raise Exception(f"Invalid prior {key} supplied")
            default_priors.update(priors)
        return default_priors

    def _assign_games(self, games):
        self.games = games
        self.n_teams = self.games["off_team_id"].unique().shape[0]
        self.team_id_to_team_ind = {
            team_id: team_ind
            for team_ind, team_id in enumerate(self.games["off_team_id"].unique())
        }
        self.team_ind_to_team_id = {
            team_ind: team_id for team_id, team_ind in self.team_id_to_team_ind.items()
        }

        self.mu_three_make_rate = (
            games["threes_made"].sum() / games["threes_attempted"].sum()
        )
        self.mu_two_make_rate = games["twos_made"].sum() / games["twos_attempted"].sum()
        self.mu_three_attempt_rate = games["threes_attempted"].sum() / (
            games["twos_attempted"].sum() + games["threes_attempted"].sum()
        )
        self.mu_ft_attempt_rate = (
            games["ft_attempted"].sum() / games["possession_num"].sum()
        )
        self.mu_ft_make_rate = games["ft_made"].sum() / games["ft_attempted"].sum()
        self.mu_off_reb_rate = games["off_rebs"].sum() / (
            games["off_rebs"].sum() + games["def_rebs"].sum()
        )
        self.mu_turnover_rate = games["turnovers"].sum() / games["possession_num"].sum()
        self.mu_pace = games["duration"].sum() / games["possession_num"].sum()
        self.mu_shot_rate = (games["threes_attempted"] + games["twos_attempted"]) / (
            games["off_rebs"] + games["possession_num"]
        )
        self.mu_attempt_rate = (
            games["twos_attempted"] + games["threes_attempted"]
        ) / games["possession_num"]
        self.mu_scoring_rate = games["points_scored"] / games["possession_num"]
        self.mu_shot_rate_est = estimate_shot_rate(
            self.mu_turnover_rate,
            self.mu_ft_attempt_rate,
        )
        self.mu_attempt_rate_est = estimate_attempt_rate(
            self.mu_shot_rate_est,
            self.mu_three_attempt_rate,
            self.mu_three_make_rate,
            self.mu_two_make_rate,
            self.mu_off_reb_rate,
        )
        self.mu_scoring_rate_est = calc_scoring_rate(
            self.mu_attempt_rate_est,
            self.mu_three_make_rate,
            self.mu_two_make_rate,
            self.mu_three_attempt_rate,
            self.mu_ft_attempt_rate,
            self.mu_ft_make_rate,
        )

    def _assign_model(self):
        off_index = self.games["off_team_id"].map(self.team_id_to_team_ind).values
        def_index = self.games["def_team_id"].map(self.team_id_to_team_ind).values
        home_index = (
            self.games["off_team_id"] != self.games["home_team_id"]
        ).values.astype(int)
        with pm.Model() as self.model:
            self._model_threes_made(off_index, def_index, home_index)
            self._model_twos_made(off_index, def_index, home_index)
            self._model_threes_attempted(off_index, def_index)
            self._model_off_rebs(off_index, def_index, home_index)
            self._model_turnovers(off_index, def_index, home_index)
            self._model_ft_attempt_rate(off_index, def_index, home_index)
            self._model_pace(off_index, def_index)
            self._model_ft_made(off_index, home_index)

    def _model_threes_made(self, off_index, def_index, home_index):
        off_three_make_rate = pm.Beta(
            "off_three_make_rate",
            mu=self.mu_three_make_rate,
            sigma=self.priors["off_three_make_rate_sigma"],
            shape=self.n_teams,
        )
        def_three_make_rate = pm.Beta(
            "def_three_make_rate",
            mu=self.mu_three_make_rate,
            sigma=self.priors["def_three_make_rate_sigma"],
            shape=self.n_teams,
        )
        home_three_make_rate = pm.Beta(
            "home_three_make_rate",
            mu=self.mu_three_make_rate + self.priors["home_three_make_rate_diff"],
            sigma=self.priors["home_three_make_rate_sigma"],
        )
        away_three_make_rate = 2 * self.mu_three_make_rate - home_three_make_rate
        games_three_make_rate = log5(
            self.mu_three_make_rate,
            off_three_make_rate[off_index],
            def_three_make_rate[def_index],
            pm.math.stack([home_three_make_rate, away_three_make_rate])[home_index],
        )
        pm.Binomial(
            "threes_made",
            n=self.games["threes_attempted"].values,
            p=games_three_make_rate,
            observed=self.games["threes_made"].values,
        )

    def _model_twos_made(self, off_index, def_index, home_index):
        off_two_make_rate = pm.Beta(
            "off_two_make_rate",
            mu=self.mu_two_make_rate,
            sigma=self.priors["off_two_make_rate_sigma"],
            shape=self.n_teams,
        )
        def_two_make_rate = pm.Beta(
            "def_two_make_rate",
            mu=self.mu_two_make_rate,
            sigma=self.priors["def_two_make_rate_sigma"],
            shape=self.n_teams,
        )
        home_two_make_rate = pm.Beta(
            "home_two_make_rate",
            mu=self.mu_two_make_rate + self.priors["home_two_make_rate_diff"],
            sigma=self.priors["home_two_make_rate_sigma"],
        )
        away_two_make_rate = 2 * self.mu_two_make_rate - home_two_make_rate
        games_two_make_rate = log5(
            self.mu_two_make_rate,
            off_two_make_rate[off_index],
            def_two_make_rate[def_index],
            pm.math.stack([home_two_make_rate, away_two_make_rate])[home_index],
        )
        pm.Binomial(
            "twos_made",
            n=self.games["twos_attempted"].values,
            p=games_two_make_rate,
            observed=self.games["twos_made"].values,
        )

    def _model_threes_attempted(self, off_index, def_index):
        off_three_attempt_rate = pm.Beta(
            "off_three_attempt_rate",
            mu=self.mu_three_attempt_rate,
            sigma=self.priors["off_three_attempt_rate_sigma"],
            shape=self.n_teams,
        )
        def_three_attempt_rate = pm.Beta(
            "def_three_attempt_rate",
            mu=self.mu_three_attempt_rate,
            sigma=self.priors["def_three_attempt_rate_sigma"],
            shape=self.n_teams,
        )
        games_three_attempt_rate = log5(
            self.mu_three_attempt_rate,
            off_three_attempt_rate[off_index],
            def_three_attempt_rate[def_index],
        )
        pm.Binomial(
            "threes_attempted",
            n=self.games["twos_attempted"].values
            + self.games["threes_attempted"].values,
            p=games_three_attempt_rate,
            observed=self.games["threes_attempted"].values,
        )

    def _model_off_rebs(self, off_index, def_index, home_index):
        off_off_reb_rate = pm.Beta(
            "off_off_reb_rate",
            mu=self.mu_off_reb_rate,
            sigma=self.priors["off_off_reb_rate_sigma"],
            shape=self.n_teams,
        )
        def_off_reb_rate = pm.Beta(
            "def_off_reb_rate",
            mu=self.mu_off_reb_rate,
            sigma=self.priors["def_off_reb_rate_sigma"],
            shape=self.n_teams,
        )
        home_off_reb_rate = pm.Beta(
            "home_off_reb_rate",
            mu=self.mu_off_reb_rate + self.priors["home_off_reb_rate_diff"],
            sigma=self.priors["home_off_reb_rate_sigma"],
        )
        away_off_reb_rate = 2 * self.mu_off_reb_rate - home_off_reb_rate
        games_off_reb_rate = log5(
            self.mu_off_reb_rate,
            off_off_reb_rate[off_index],
            def_off_reb_rate[def_index],
            pm.math.stack([home_off_reb_rate, away_off_reb_rate])[home_index],
        )
        pm.Binomial(
            "off_rebs",
            n=self.games["off_rebs"].values + self.games["def_rebs"].values,
            p=games_off_reb_rate,
            observed=self.games["off_rebs"].values,
        )

    def _model_turnovers(self, off_index, def_index, home_index):
        off_turnover_rate = pm.Beta(
            "off_turnover_rate",
            mu=self.mu_turnover_rate,
            sigma=self.priors["off_turnover_rate_sigma"],
            shape=self.n_teams,
        )
        def_turnover_rate = pm.Beta(
            "def_turnover_rate",
            mu=self.mu_turnover_rate,
            sigma=self.priors["def_turnover_rate_sigma"],
            shape=self.n_teams,
        )
        home_turnover_rate = pm.Beta(
            "home_turnover_rate",
            mu=self.mu_turnover_rate - self.priors["home_turnover_rate_diff"],
            sigma=self.priors["home_turnover_rate_sigma"],
        )
        away_turnover_rate = 2 * self.mu_turnover_rate - home_turnover_rate
        games_turnover_rate = log5(
            self.mu_turnover_rate,
            off_turnover_rate[off_index],
            def_turnover_rate[def_index],
            pm.math.stack([home_turnover_rate, away_turnover_rate])[home_index],
        )
        pm.Binomial(
            "turnovers",
            n=self.games["possession_num"].values,
            p=games_turnover_rate,
            observed=self.games["turnovers"].values,
        )

    def _model_ft_attempt_rate(self, off_index, def_index, home_index):
        off_ft_attempt_rate = pm.Gamma(
            "off_ft_attempt_rate",
            mu=self.mu_ft_attempt_rate,
            sigma=self.priors["off_ft_attempt_rate_sigma"],
            shape=self.n_teams,
        )
        def_ft_attempt_rate = pm.Gamma(
            "def_ft_attempt_rate",
            mu=self.mu_ft_attempt_rate,
            sigma=self.priors["def_ft_attempt_rate_sigma"],
            shape=self.n_teams,
        )
        home_ft_attempt_rate = pm.Gamma(
            "home_ft_attempt_rate",
            mu=self.mu_ft_attempt_rate + self.priors["home_ft_attempt_rate_diff"],
            sigma=self.priors["home_ft_attempt_rate_sigma"],
        )
        away_ft_attempt_rate = 2 * self.mu_ft_attempt_rate - home_ft_attempt_rate
        games_ft_attempt_rate = log5(
            self.mu_ft_attempt_rate,
            off_ft_attempt_rate[off_index],
            def_ft_attempt_rate[def_index],
            pm.math.stack([home_ft_attempt_rate, away_ft_attempt_rate])[home_index],
        )
        sigma_ft_attempt_rate = pm.Gamma(
            "sigma_ft_attempt_rate",
            mu=self.priors["sigma_ft_attempt_rate_mu"],
            sigma=self.priors["sigma_ft_attempt_rate_sigma"],
        )
        pm.Normal(
            "ft_attempt_rate",
            mu=games_ft_attempt_rate,
            sigma=sigma_ft_attempt_rate,
            observed=self.games["ft_attempt_rate"].values,
        )

    def _model_pace(self, off_index, def_index):
        off_pace = pm.Gamma(
            "off_pace",
            mu=self.mu_pace,
            sigma=self.priors["off_pace_sigma"],
            shape=self.n_teams,
        )
        def_pace = pm.Gamma(
            "def_pace",
            mu=self.mu_pace,
            sigma=self.priors["def_pace_sigma"],
            shape=self.n_teams,
        )
        games_pace = log5(
            self.mu_pace,
            off_pace[off_index],
            def_pace[def_index],
        )
        sigma_pace = pm.Gamma(
            "sigma_pace",
            mu=self.priors["sigma_pace_mu"],
            sigma=self.priors["sigma_pace_sigma"],
        )
        pm.Gamma(
            "pace",
            mu=games_pace,
            sigma=sigma_pace,
            observed=self.games["pace"].values,
        )

    def _model_ft_made(self, off_index, home_index):
        off_ft_make_rate = pm.Beta(
            "off_ft_make_rate",
            mu=self.mu_ft_make_rate,
            sigma=self.priors["off_ft_make_rate_sigma"],
            shape=self.n_teams,
        )
        home_ft_make_rate = pm.Gamma(
            "home_ft_make_rate",
            mu=self.mu_ft_make_rate + self.priors["home_ft_make_rate_diff"],
            sigma=self.priors["home_ft_make_rate_sigma"],
        )
        away_ft_make_rate = 2 * self.mu_ft_make_rate - home_ft_make_rate
        games_ft_make_rate = log5(
            self.mu_ft_make_rate,
            off_ft_make_rate[off_index],
            pm.math.stack([home_ft_make_rate, away_ft_make_rate])[home_index],
        )
        pm.Binomial(
            "ft_made",
            n=self.games["ft_attempted"].values,
            p=games_ft_make_rate,
            observed=self.games["ft_made"].values,
        )

    def fit(self, steps=5000, init="adapt_diag", **kwargs):
        """
        Fit PyMC3 model to provided data. This is a wrapper of
        pm.sample with some defaults.
        """
        with self.model:
            self._trace = pm.sample(steps, init=init, **kwargs)
            self._results = self._calc_results()

    @property
    def trace(self):
        """Property method to get PyMC3 model trace"""
        try:
            return self._trace
        except AttributeError as exc:
            raise Exception(
                "Trace only available after fitting the model with the fit method"
            ) from exc

    @property
    def results(self):
        """Property method to get post-processed model results"""
        try:
            return self._results
        except AttributeError as exc:
            raise Exception(
                "Results only available after fitting the model with the fit method"
            ) from exc

    def _calc_results(self):
        off_shot_rate_est = estimate_shot_rate(
            self.trace["off_turnover_rate"],
            self.trace["off_ft_attempt_rate"],
        )
        off_attempt_rate_est = estimate_attempt_rate(
            off_shot_rate_est,
            self.trace["off_three_attempt_rate"],
            self.trace["off_three_make_rate"],
            self.trace["off_two_make_rate"],
            self.trace["off_off_reb_rate"],
        )
        off_scoring_rate_est = calc_scoring_rate(
            off_attempt_rate_est,
            self.trace["off_three_make_rate"],
            self.trace["off_two_make_rate"],
            self.trace["off_three_attempt_rate"],
            self.trace["off_ft_attempt_rate"],
            self.trace["off_ft_make_rate"],
        )

        def_shot_rate_est = estimate_shot_rate(
            self.trace["def_turnover_rate"],
            self.trace["def_ft_attempt_rate"],
        )
        def_attempt_rate_est = estimate_attempt_rate(
            def_shot_rate_est,
            self.trace["def_three_attempt_rate"],
            self.trace["def_three_make_rate"],
            self.trace["def_two_make_rate"],
            self.trace["def_off_reb_rate"],
        )
        def_scoring_rate_est = calc_scoring_rate(
            def_attempt_rate_est,
            self.trace["def_three_make_rate"],
            self.trace["def_two_make_rate"],
            self.trace["def_three_attempt_rate"],
            self.trace["def_ft_attempt_rate"],
            self.mu_ft_make_rate,
        )

        results = pd.DataFrame()
        results["team"] = [
            team_id_to_team_abb[self.team_ind_to_team_id[ind]]
            for ind in range(self.trace["off_pace"].shape[1])
        ]
        results["off_three_attempt_rate"] = (
            self.trace["off_three_attempt_rate"].mean(0) * 100
        )
        results["off_two_make_rate"] = self.trace["off_two_make_rate"].mean(0) * 100
        results["off_three_make_rate"] = self.trace["off_three_make_rate"].mean(0) * 100
        results["off_reb_rate"] = self.trace["off_off_reb_rate"].mean(0) * 100
        results["off_turnover_rate"] = self.trace["off_turnover_rate"].mean(0) * 100
        results["off_ft_attempt_rate"] = self.trace["off_ft_attempt_rate"].mean(0) * 100
        results["off_ft_make_rate"] = self.trace["off_ft_make_rate"].mean(0) * 100
        results["def_three_attempt_rate"] = (
            self.trace["def_three_attempt_rate"].mean(0) * 100
        )
        results["def_two_make_rate"] = self.trace["def_two_make_rate"].mean(0) * 100
        results["def_three_make_rate"] = self.trace["def_three_make_rate"].mean(0) * 100
        results["def_reb_rate"] = (1 - self.trace["def_off_reb_rate"].mean(0)) * 100
        results["def_turnover_rate"] = self.trace["def_turnover_rate"].mean(0) * 100
        results["def_ft_attempt_rate"] = self.trace["def_ft_attempt_rate"].mean(0) * 100
        results["off_scoring_rate"] = off_scoring_rate_est.mean(0) * 100
        results["def_scoring_rate"] = def_scoring_rate_est.mean(0) * 100
        results["net_scoring_rate"] = (
            results["off_scoring_rate"] - results["def_scoring_rate"]
        )
        results["off_pace"] = (12 * 4 * 60 / self.trace["off_pace"] / 2).mean(0)
        results["def_pace"] = (12 * 4 * 60 / self.trace["def_pace"] / 2).mean(0)
        results["total_pace"] = (
            12 * 4 * 60 / (self.trace["off_pace"] + self.trace["def_pace"])
        ).mean(0)
        results["scoring_margin"] = (
            results["net_scoring_rate"] * results["total_pace"] / 100
        )
        results = results.sort_values("scoring_margin", ascending=False)
        return results

    def traceplot(self):
        """Simple wrapper for pm.traceplot"""
        pm.traceplot(self.trace)

    def plot_ratings(self, axis):
        """Plot team off/def ratings on the provided axis"""
        off_rating = self.results["off_scoring_rate"] - self.mu_scoring_rate_est * 100
        def_rating = self.mu_scoring_rate_est * 100 - self.results["def_scoring_rate"]

        plot_logos(off_rating, def_rating, self.results["team"], axis, size=30)
        axis.set_xlabel("Offensive Rating (pts/poss)")
        axis.set_ylabel("Defensive Rating (pts/poss)")

    def plot_paces(self, axis):
        """Plot team off/def pace on the provided axis"""
        plot_logos(
            self.results["off_pace"],
            self.results["def_pace"],
            self.results["team"],
            axis,
            size=30,
        )
        axis.set_xlabel("Offensive Pace (poss/48)")
        axis.set_ylabel("Defensive Pace (poss/48)")


def log5(mean, *args):
    """Calculate expected value given mean and samples from the population"""
    odds0 = mean / (1 - mean)
    odds = args[0] / (1 - args[0]) / odds0 ** (len(args) - 1)
    for arg in args[1:]:
        odds *= arg / (1 - arg)
    return odds / (odds + 1)
