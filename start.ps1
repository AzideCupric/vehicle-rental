$env:FLASK_APP = "rentalos"
$env:FLASK_ENV = "development"
flask init-db
flask run