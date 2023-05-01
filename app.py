from components import App

if __name__ == '__main__':
    app = App()
    server = app.app.server
    app.run_app()
