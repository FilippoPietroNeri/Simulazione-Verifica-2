import base64
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from flask import Flask, render_template, request, redirect
app = Flask(__name__)

df = pd.read_excel(
    'https://github.com/wtitze/3E/blob/main/BikeStores.xls?raw=true', sheet_name='customers')
clients_per_state = df.groupby('state').count().reset_index()

@app.route('/')
def home():
    error = request.args.get('error')
    return render_template('index.html', error=error)


@app.route('/res/<id>/')
def api_result(id):
    match int(id):
        case 1:
            fname = request.args.get('first_name')
            lname = request.args.get('last_name')
            result = df[(df.first_name == fname) & (df.last_name == lname)]
            return render_template('result.html', products=result.to_html())
        case 2:
            city = request.args.get('city')
            result = df[df.city == city]
            return render_template('result.html', products=result.to_html())
        case 3:
            result = clients_per_state[['state', 'customer_id']]
            return render_template('result.html', products=result.to_html())
        case 4:
            result = clients_per_state[clients_per_state['customer_id']
                == clients_per_state['customer_id'].max()]
            return render_template('result.html', products=result.to_html())
        case 5:
            # BARRE VERTICALI
            fig1, ax1 = plt.subplots(figsize=(10, 8))
            ax1.bar(clients_per_state['state'],clients_per_state['customer_id'], label='Numero Clienti')
            ax1.set_ylabel('Numero di Clienti')
            ax1.set_xlabel('Stati')
            ax1.set_title('Numero di clienti per ogni stato')
            ax1.legend()
            plt.xticks(rotation=90, fontsize=15)

            #Create Buffer for Image
            buf1 = BytesIO()
            fig1.savefig(buf1, format="png")
            data1 = base64.b64encode(buf1.getbuffer()).decode("ascii")

            # BARRE ORIZZONTALI
            fig2,ax2 = plt.subplots(figsize=(10,8))
            ax2.barh(clients_per_state['state'],clients_per_state['customer_id'],label='Numero Clienti')
            ax2.set_ylabel('Numero di Clienti')
            ax2.set_xlabel('Stati')
            ax2.set_title('Numero di clienti per ogni stato')
            ax2.legend()

            #Create Buffer for Image
            buf2 = BytesIO()
            fig2.savefig(buf2, format="png")
            data2 = base64.b64encode(buf2.getbuffer()).decode("ascii")

            # TORTA
            fig3 = plt.figure(figsize=(10,8))
            plt.pie(clients_per_state['customer_id'],labels=clients_per_state['state'], autopct='%1.1f%%')
            plt.show()
            
            #Create Buffer for Image
            buf3 = BytesIO()
            fig3.savefig(buf3, format="png")
            data3 = base64.b64encode(buf3.getbuffer()).decode("ascii")

            return render_template('result_img.html', image=f'data:image/png;base64,{data1}', image2=f'data:image/png;base64,{data2}', image3=f'data:image/png;base64,{data3}' )
        case 6:
            result = df[df['email'].isna()][['first_name', 'last_name', 'phone']]
            return render_template('result.html', products=result.to_html())
        case 7:
            provider = request.args.get('provider')
            if len(provider) == 0:
                return redirect('/?error=Non hai specificato un provider')
            result = df[df.email.str.endswith(f'@{provider}', na=False)][['first_name','last_name']]
            if len(result) == 0:
                return redirect('/?error=Nessuno ha questo provider')
            return render_template('result.html', products=result.to_html())
        case _:
            return redirect('/?error=Esercizio non trovato')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3245, debug=True)
