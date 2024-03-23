import os
import jwt



from shop import create_app, db


app = create_app("default")

# db.create_all()


@app.shell_context_processor
def make_shellprocessor():
    return dict(db=db)




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        

    app.run(debug=True)
