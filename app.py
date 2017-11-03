from flask import Flask, render_template, request, send_file
from mymetrics.sbi_trade_history import (
    rearrange_trade_data, evaluate_risk_reward
)
from mymetrics.analytics import track_event
import pandas as pd
from io import BytesIO


app = Flask(__name__)


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


@app.route('/sbi')
def sbi():
    """ analyze sbi history """
    track_event('sbi', 'get')

    buttons = [
        # ('plt', 'グラフ'),
        ('rr', 'RR分析'),
        ('rearrange', 'データ整形'),
    ]
    return render_template('sbi.html', buttons=buttons)


@app.route('/sbi_button', methods=['POST'])
def sbi_button():
    """ calculate sbi risk riward """
    # import pdb;  pdb.set_trace()

    ifile = request.files['file']
    df = pd.read_csv(ifile, encoding='Shift-JIS', skiprows=5)
    res = rearrange_trade_data(df)

    if request.form['action'] == 'plt':
        track_event('sbi', 'plt')
        return 'plot graph(in test stage)'
    elif request.form['action'] == 'rr':
        track_event('sbi', 'rr')
        rr = evaluate_risk_reward(res)
        ofile = pd.DataFrame(rr).to_csv().encode('utf-8')
        return send_file(BytesIO(ofile),
                         attachment_filename='RiskReward.csv',
                         as_attachment=True)
    elif request.form['action'] == 'rearrange':
        track_event('sbi', 'rearrange')
        ofile = res.to_csv().encode('utf-8')
        return send_file(BytesIO(ofile), attachment_filename='SBIhistory.csv',
                         as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
