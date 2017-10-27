from cook import core, android

app = android.native_app(
    name='app',
    sources=core.glob('src/**/*.cpp'),
)
core.default(app)

android.install(
    name='upload',
    app=app,
    launch=True
)
