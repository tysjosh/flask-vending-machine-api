from src import create_app
from src.models import db
from flask_migrate import upgrade, migrate, init, stamp



def deploy():
	"""Run deployment tasks."""
	app = create_app()
	app.app_context().push()
	db.create_all()

	# migrate database to latest revision
	init()
	stamp()
	migrate()
	upgrade()
	
deploy()