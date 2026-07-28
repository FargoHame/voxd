def test_app_import_does_not_require_voicehub():
    from hubaks.main import create_app

    app = create_app()

    assert app.title == "Hubaks Runtime"
    assert app.version == "1.5.0"


def test_app_mounts_without_built_web_assets():
    from hubaks.main import create_app

    app = create_app()

    assert app is not None
