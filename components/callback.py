from dash import Output, Input, State, callback


class Callback:
    def __init__(self, func, outputs: list, inputs: list, states: list = None, initial_call: bool = False):
        self.func = func
        self.prevent_initial_call = True if initial_call is False else False
        self.outputs = [Output(outp[0], outp[1]) for outp in outputs]
        self.inputs = [Input(inp[0], inp[1]) for inp in inputs]
        self.states = [State(st[0], st[1]) for st in states] if states else []
        self.callback = callback(
            *self.outputs, *self.inputs, *self.states,
            prevent_initial_call=self.prevent_initial_call
        )(self.func)
