from UPISAS.strategy import Strategy
import UPISAS.exemplars.switch as switch


def convert(model):
    # maps input rate to idea model
    return model
    pass


class SwitchStrategy(Strategy):

    def analyze(self):
        data = switch.get_monitor_data()
        print(data)
        self.knowledge.analysis_data['input_rate'] = data['input_rate']
        self.knowledge.analysis_data['current_model'] = data['model']

    def plan(self):
        input_rate = self.knowledge.analysis_data['input_rate']
        model = self.knowledge.analysis_data['current_model']
        ideal_model = convert(model)
        if input_rate > convert(model):
            print("Switching from model {} to model {}", model, ideal_model)
            self.knowledge.analysis_data['ideal_model'] = ideal_model
        return True
