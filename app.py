from components import App

app = App()
server = app.app.server

if __name__ == '__main__':
    app.run_app()
