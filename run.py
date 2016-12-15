from mainapp import app
app.secret_key = 'secret'
if __name__ == '__main__':
    app.run(debug = True)
