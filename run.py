from flask import Flask, render_template, request, send_file  # noqa
from applications import sbi, vain
from mymetrics.analytics import track_event
from mymetrics.environment import if_is_development
# デバッグをしたい場合
# import pdb;  pdb.set_trace()


app = Flask(__name__)
for m in [sbi.mod, vain.mod, ]:
    app.register_blueprint(m)


@app.route('/')
@app.route('/about')
def about():
    """ about """
    track_event('about', 'get')

    accounts = [
        ('Qiita', 'https://qiita.com/qiugits'),
        ('Github', 'https://github.com/qiugits'),
    ]
    return render_template('about.html', accounts=accounts)


if __name__ == '__main__':
    app.run(debug=if_is_development())