from flask import Flask, render_template, request, jsonify, render_template, session, make_response, Markup, send_from_directory
import os
from datetime import datetime
import vol2, malzclass

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route("/ManualDashboard", methods=["POST", "GET"])
def manual():
    file_path = os.path.abspath(__file__).replace('\\', '/')
    if request.method == "POST":
        file = request.files['file']
        file_name = os.path.abspath(file.filename)
        upload_directory = os.path.join(app.root_path)
        file_path = os.path.join(upload_directory, file_name)
        file.save(file_path)
        session["filePath"] = file_path
        return make_response('', 204)
    else:
        return render_template("ManualDashboard.html", file_path=file_path)


@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route("/AutoDashboard", methods=["POST", "GET"])
def auto():
    file_path = os.path.abspath(__file__).replace('\\', '/')
    if request.method == "POST":
        file = request.files['file']
        file_name = os.path.abspath(file.filename)
        upload_directory = os.path.join(app.root_path)
        file_path = os.path.join(upload_directory, file_name)
        file.save(file_path)
        session["filePath"] = file_path
        return make_response('', 204)
    else:
        return render_template("AutoDashboard.html", file_path=file_path)


@app.route('/generate_report', methods=['POST'])
def generate_report():
    manDict = request.json
    

    with open('templates/generateReport.html', 'r') as template_file:
        template_content = template_file.read()

    # Isi template dengan konten yang diinginkan
    # Misalnya, Anda dapat menggunakan Jinja untuk mengganti placeholder dengan nilai yang diinginkan
    # Di sini, kita hanya akan mengganti placeholder {{ content }} dengan string "Ini adalah konten yang diinginkan"
    html_content = template_content.replace('{{ name }}', 'wanncry.vmem')
    html_content = html_content.replace('{{ size }}', '7 GB')
    html_content = html_content.replace('{{ hash }}', '1h43556789')
    html_content = html_content.replace('{{ optsys }}', 'Windows')
    html_content = html_content.replace('{{ lname }}', 'Windows Intel')
    html_content = html_content.replace('{{ lmemory }}', '1 File Layer')
    html_content = html_content.replace('{{ proc }}', 'x64')
    html_content = html_content.replace(
        '{{ systime }}', '2023-06-16  02:25:51')
    html_content = html_content.replace('{{ sysroot }}', 'c:\windows')

    # Pslist==================================================================================
    pslist_data = manDict.get('windows.pslist.PsList',{})
    
    if 'windows.pslist.PsList' in manDict:
        header1_values = None
        for value in pslist_data.values():
            if isinstance(value, list):
                header1_values = value
                break
        num_header1_values = len(header1_values)
        num_keys_key1 = len(pslist_data)
        pslist_content = ''
        for value in pslist_data.values():
            counter = 0
            print(value)
            pslist_row = '<tr>'
            print(f"key: {value[6]}")
            for indexval in range(num_header1_values):
                if counter == 11:
                    break
                print(f"value({str(indexval)}): {value[indexval]}")
                pslist_row += f'<td>{value[indexval]}</td>'
                counter+=1
            pslist_row += '</tr>'
            pslist_content += pslist_row
        html_content = html_content.replace('{PSLIST_CONTENT}', pslist_content)
    
    

    # Tentukan direktori tujuan untuk menyimpan file HTML yang diunduh
    destination_directory = os.path.join(os.getcwd(), 'static', 'reports')
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    # Simpan file HTML di direktori tujuan
    tanggal_waktu_sekarang = datetime.now()
    deretan_angka = tanggal_waktu_sekarang.strftime('%Y%m%d%H%M%S')
    report_filename = 'report ' + deretan_angka + '.html'
    session["fileName"] = report_filename
    report_path = os.path.join(destination_directory, report_filename)
    with open(report_path, 'w') as report_file:
        report_file.write(html_content)

    # Kembalikan file HTML yang diunduh
    response = make_response(html_content)
    response.headers['Content-Disposition'] = 'attachment; filename=data.html'
    response.headers['Content-type'] = 'text/html'

    return response


@app.route('/processAuto', methods=['POST'])
def process_formAuto():
    autoDict = {}
    autoDict.clear()
    malware = request.form.get('malware')
    filePath = session.get('filePath')
    if malware == "wannacry":
        t = malzclass.WannaCry(filepath=filePath, outputpath="./outputtest")
        autoDict = t.run()
    elif malware == "emotet":
        pass
    elif malware == "stuxnet":
        pass
    print(autoDict)
    html_content = generate_html(autoDict)
    tanggal_waktu_sekarang = datetime.now()
    deretan_angka = tanggal_waktu_sekarang.strftime('%Y-%m-%d_%H%M%S')
    # Menyimpan file HTML di folder /static/reports
    filename = "data_" + deretan_angka + ".html"
    session["fileName"] = filename
    save_path = os.path.join(app.static_folder, 'reports')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    file_path = os.path.join(save_path, filename)

    with open(file_path, 'w') as file:
        file.write(html_content)

    # Mengirimkan file HTML yang akan diunduh
    response = make_response(html_content)
    response.headers['Content-Disposition'] = 'attachment; filename=data.html'
    response.headers['Content-type'] = 'text/html'

    return response

@app.route('/open_report', methods=['GET'])
def open_report():
    filename = session.get('fileName')  # Ganti dengan nama file HTML yang ingin dibuka
    return send_from_directory('static/reports', filename)

def generate_html(data):
    html = "<html><body>"
    html += "<h1>Data Dictionary</h1>"
    html += "<table>"
    for key, value in data.items():
        html += "<tr><td>{}</td><td>{}</td></tr>".format(key, value)
    html += "</table>"
    html += "</body></html>"

    return Markup(html)

@app.route('/process-form', methods=['POST'])
def process_form():
    # command = request.form["command"]
    # filePath = request.form["file-path"]
    # pid = request.form["pid-fieldvalue"]
    # offset = request.form["offset-fieldvalue"]
    # key = request.form["key-fieldvalue"]
    # physical = request.form.get("physical-check")
    # includeCorrupt = request.form.get("include-corruptCheck")
    # recurse = request.form.get("recurseCheck")
    # dump = request.form.get("dumpCheck")

    # if physical is None:
    #     physical = False

    # if includeCorrupt is None:
    #     includeCorrupt = False

    # if recurse is None:
    #     recurse = False

    # if dump is None:
    #     dump = False
    form_data = request.form
    command = ""
    filePath = session.get('filePath')
    pid = ""
    offset = ""
    keyRegis = ""
    physical = ""
    includeCorrupt = ""
    recurse = ""
    dump = ""

    data_dict = {}
    data_dict.clear()
    for key, value in form_data.items():
        if key == "command":
            command = value
        # elif key == "file-path":
        #     filePath = "./"+value
        elif key == "pid-fieldvalue":
            pid = value
        elif key == "offset-fieldvalue":
            offset = value
        elif key == "key-fieldvalue":
            keyRegis = value
        elif key == "physical-check":
            physical = value
        elif key == "include-corruptCheck":
            includeCorrupt = value
        elif key == "recurseCheck":
            recurse = value
        elif key == "dumpCheck":
            dump = value

    print(command)
    data_dict = vol2.run(command,filePath,"./outputtest",[])
    # data_dict = vol2.run("windows.psscan.PsScan","./wanncry.vmem","./outputtest",[])
    # print("File: "+filePath)
    print(data_dict)
    return jsonify(data_dict)

    # "File: "+ return jsonify({"command": command, "File Path": filePath, "PID": pid, "Offset": offset, "Key": key, "Include Corrupt": includeCorrupt, "Recurse": recurse, "Dump": dump,  "physic": physical})


@app.route("/<cmd>")
def commandtest(cmd):
    return f"<h1>{cmd}</h1>"


if __name__ == "__main__":
    app.run(debug=True)
