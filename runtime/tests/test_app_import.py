def test_app_import_does_not_require_voicehub():
    from voxd.main import create_app

    app = create_app()

    assert app.title == "Voxd Runtime"
