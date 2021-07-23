"""Model team statistics"""

import pandas as pd
import pymc3 as pm

from pynba import team_id_to_abb
from pynba.halfgames import (
    estimate_shots_per_opp,
    estimate_shots_per_poss,
    calc_scoring_rate,
)
from pynba.config import config


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

    def __init__(self, halfgames, priors=None):
        self.priors = self._process_priors(priors)
        self._assign_halfgames(halfgames)
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

    def _assign_halfgames(self, halfgames):
        self.halfgames = halfgames
        self.n_teams = self.halfgames["off_team_id"].unique().shape[0]
        self.team_id_to_team_ind = {
            team_id: team_ind
            for team_ind, team_id in enumerate(self.halfgames["off_team_id"].unique())
        }

        self.league = self.halfgames["league"].iloc[0]
        self.year = self.halfgames["year"].iloc[0]
        self.season_type = "+".join(
            sorted(self.halfgames["season_type"].unique(), reverse=True)
        )
        team_id_to_team_abb = team_id_to_abb(self.league, self.year)
        self.team_ind_to_team_abb = {
            team_ind: team_id_to_team_abb[team_id]
            for team_id, team_ind in self.team_id_to_team_ind.items()
        }

        self.mu_three_make_rate = (
            self.halfgames["threes_made"].sum()
            / self.halfgames["threes_attempted"].sum()
        )
        self.mu_two_make_rate = (
            self.halfgames["twos_made"].sum() / self.halfgames["twos_attempted"].sum()
        )
        self.mu_three_attempt_rate = self.halfgames["threes_attempted"].sum() / (
            self.halfgames["twos_attempted"].sum()
            + self.halfgames["threes_attempted"].sum()
        )
        self.mu_ft_attempt_rate = (
            self.halfgames["ft_attempted"].sum()
            / self.halfgames["possession_num"].sum()
        )
        self.mu_ft_make_rate = (
            self.halfgames["ft_made"].sum() / self.halfgames["ft_attempted"].sum()
        )
        self.mu_off_reb_rate = self.halfgames["off_rebs"].sum() / (
            self.halfgames["off_rebs"].sum() + self.halfgames["def_rebs"].sum()
        )
        self.mu_turnover_rate = (
            self.halfgames["turnovers"].sum() / self.halfgames["possession_num"].sum()
        )
        self.mu_pace = (
            self.halfgames["duration"].sum() / self.halfgames["possession_num"].sum()
        )
        self.mu_shots_per_opp = (
            self.halfgames["threes_attempted"] + self.halfgames["twos_attempted"]
        ).sum() / (self.halfgames["off_rebs"] + self.halfgames["possession_num"]).sum()
        self.mu_shots_per_poss = (
            self.halfgames["twos_attempted"] + self.halfgames["threes_attempted"]
        ).sum() / self.halfgames["possession_num"].sum()
        self.mu_scoring_rate = (
            self.halfgames["points_scored"].sum()
            / self.halfgames["possession_num"].sum()
        )
        self.mu_shots_per_opp_est = estimate_shots_per_opp(
            self.mu_turnover_rate,
            self.mu_ft_attempt_rate,
        )
        self.mu_shots_per_poss_est = estimate_shots_per_poss(
            self.mu_shots_per_opp_est,
            self.mu_three_attempt_rate,
            self.mu_three_make_rate,
            self.mu_two_make_rate,
            self.mu_off_reb_rate,
        )
        self.mu_scoring_rate_est = calc_scoring_rate(
            self.mu_shots_per_poss_est,
            self.mu_three_make_rate,
            self.mu_two_make_rate,
            self.mu_three_attempt_rate,
            self.mu_ft_attempt_rate,
            self.mu_ft_make_rate,
        )

    def _assign_model(self):
        self.model = pm.Model()
        off_index = (
            self.halfgames["off_team_id"].map(self.team_id_to_team_ind).to_numpy()
        )
        def_index = (
            self.halfgames["def_team_id"].map(self.team_id_to_team_ind).to_numpy()
        )
        home_index = (
            (self.halfgames["off_team_id"] != self.halfgames["home_team_id"])
            .to_numpy()
            .astype(int)
        )
        with self.model:
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
        halfgames_three_make_rate = log5(
            self.mu_three_make_rate,
            off_three_make_rate[off_index],
            def_three_make_rate[def_index],
            pm.math.stack([home_three_make_rate, away_three_make_rate])[home_index],
        )
        pm.Binomial(
            "threes_made",
            n=self.halfgames["threes_attempted"].to_numpy(),
            p=halfgames_three_make_rate,
            observed=self.halfgames["threes_made"].to_numpy(),
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
        halfgames_two_make_rate = log5(
            self.mu_two_make_rate,
            off_two_make_rate[off_index],
            def_two_make_rate[def_index],
            pm.math.stack([home_two_make_rate, away_two_make_rate])[home_index],
        )
        pm.Binomial(
            "twos_made",
            n=self.halfgames["twos_attempted"].to_numpy(),
            p=halfgames_two_make_rate,
            observed=self.halfgames["twos_made"].to_numpy(),
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
        halfgames_three_attempt_rate = log5(
            self.mu_three_attempt_rate,
            off_three_attempt_rate[off_index],
            def_three_attempt_rate[def_index],
        )
        pm.Binomial(
            "threes_attempted",
            n=(
                self.halfgames["twos_attempted"] + self.halfgames["threes_attempted"]
            ).to_numpy(),
            p=halfgames_three_attempt_rate,
            observed=self.halfgames["threes_attempted"].to_numpy(),
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
        halfgames_off_reb_rate = log5(
            self.mu_off_reb_rate,
            off_off_reb_rate[off_index],
            def_off_reb_rate[def_index],
            pm.math.stack([home_off_reb_rate, away_off_reb_rate])[home_index],
        )
        pm.Binomial(
            "off_rebs",
            n=(self.halfgames["off_rebs"] + self.halfgames["def_rebs"]).to_numpy(),
            p=halfgames_off_reb_rate,
            observed=self.halfgames["off_rebs"].to_numpy(),
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
        halfgames_turnover_rate = log5(
            self.mu_turnover_rate,
            off_turnover_rate[off_index],
            def_turnover_rate[def_index],
            pm.math.stack([home_turnover_rate, away_turnover_rate])[home_index],
        )
        pm.Binomial(
            "turnovers",
            n=self.halfgames["possession_num"].to_numpy(),
            p=halfgames_turnover_rate,
            observed=self.halfgames["turnovers"].to_numpy(),
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
        halfgames_ft_attempt_rate = log5(
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
            mu=halfgames_ft_attempt_rate,
            sigma=sigma_ft_attempt_rate,
            observed=self.halfgames["ft_attempt_rate"].to_numpy(),
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
        halfgames_pace = log5(
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
            mu=halfgames_pace,
            sigma=sigma_pace,
            observed=self.halfgames["pace"].to_numpy(),
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
        halfgames_ft_make_rate = log5(
            self.mu_ft_make_rate,
            off_ft_make_rate[off_index],
            pm.math.stack([home_ft_make_rate, away_ft_make_rate])[home_index],
        )
        pm.Binomial(
            "ft_made",
            n=self.halfgames["ft_attempted"].to_numpy(),
            p=halfgames_ft_make_rate,
            observed=self.halfgames["ft_made"].to_numpy(),
        )

    def fit(
        self,
        draws=config.pymc3_draws,
        init=config.pymc3_init,
        chains=config.pymc3_chains,
        random_seed=config.pymc3_random_seed,
        return_inferencedata=False,
        **kwargs,
    ):
        """
        Fit PyMC3 model to provided data. This is a wrapper of
        pm.sample with some defaults.
        """
        with self.model:
            self._trace = pm.sample(
                draws=draws,
                init=init,
                chains=chains,
                random_seed=random_seed,
                return_inferencedata=return_inferencedata,
                **kwargs,
            )
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
        off_shots_per_opp_est = estimate_shots_per_opp(
            self.trace["off_turnover_rate"],
            self.trace["off_ft_attempt_rate"],
        )
        off_shots_per_poss_est = estimate_shots_per_poss(
            off_shots_per_opp_est,
            self.trace["off_three_attempt_rate"],
            self.trace["off_three_make_rate"],
            self.trace["off_two_make_rate"],
            self.trace["off_off_reb_rate"],
        )
        off_scoring_rate_est = calc_scoring_rate(
            off_shots_per_poss_est,
            self.trace["off_three_make_rate"],
            self.trace["off_two_make_rate"],
            self.trace["off_three_attempt_rate"],
            self.trace["off_ft_attempt_rate"],
            self.trace["off_ft_make_rate"],
        )

        def_shots_per_opp_est = estimate_shots_per_opp(
            self.trace["def_turnover_rate"],
            self.trace["def_ft_attempt_rate"],
        )
        def_shots_per_poss_est = estimate_shots_per_poss(
            def_shots_per_opp_est,
            self.trace["def_three_attempt_rate"],
            self.trace["def_three_make_rate"],
            self.trace["def_two_make_rate"],
            self.trace["def_off_reb_rate"],
        )
        def_scoring_rate_est = calc_scoring_rate(
            def_shots_per_poss_est,
            self.trace["def_three_make_rate"],
            self.trace["def_two_make_rate"],
            self.trace["def_three_attempt_rate"],
            self.trace["def_ft_attempt_rate"],
            self.mu_ft_make_rate,
        )

        results = pd.DataFrame()
        results["team"] = [
            self.team_ind_to_team_abb[ind]
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
        results["off_scoring_above_average"] = (
            results["off_scoring_rate"] - self.mu_scoring_rate_est * 100
        )
        results["def_scoring_above_average"] = (
            self.mu_scoring_rate_est * 100 - results["def_scoring_rate"]
        )
        results["net_scoring_rate"] = (
            results["off_scoring_rate"] - results["def_scoring_rate"]
        )
        results["off_pace"] = (12 * 4 * 60 / self.trace["off_pace"] / 2).mean(0)
        results["def_pace"] = (12 * 4 * 60 / self.trace["def_pace"] / 2).mean(0)
        results["off_pace_above_average"] = (
            results["off_pace"] - results["off_pace"].mean()
        )
        results["def_pace_above_average"] = (
            results["def_pace"] - results["def_pace"].mean()
        )
        results["total_pace"] = (
            12 * 4 * 60 / (self.trace["off_pace"] + self.trace["def_pace"])
        ).mean(0)
        results["scoring_margin"] = (
            results["net_scoring_rate"] * results["total_pace"] / 100
        )
        results = results.sort_values("scoring_margin", ascending=False)
        results["league"] = self.league
        results["year"] = self.year
        results["season_type"] = self.season_type
        return results

    def traceplot(self):
        """Wrapper for pm.traceplot"""
        pm.traceplot(self.trace)


def log5(mean, *args):
    """Calculate expected value given mean and samples from the population"""
    odds0 = mean / (1 - mean)
    odds = args[0] / (1 - args[0]) / odds0 ** (len(args) - 1)
    for arg in args[1:]:
        odds *= arg / (1 - arg)
    return odds / (odds + 1)
