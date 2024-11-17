from UPISAS.strategies.SwitchStrategy import SwitchStrategy
# from UPISAS.exemplars.switch import switch


def before_run(self) -> None:
    """Perform any activity required before starting a run.
    No context is available here as the run is not yet active (BEFORE RUN)"""
    # self.exemplar = switch()
    self.strategy = SwitchStrategy(self.exemplar)
