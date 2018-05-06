import numpy as np
import pandas as pd

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

# from sqlalchemy.ext.automap import automap_base
# from sqlalchemy.orm import Session
# from sqlalchemy import create_engine, func

# engine = create_engine("sqlite:///DataSets/belly_button_biodiversity.sqlite")

# # reflect an existing database into a new model
# Base = automap_base()
# # reflect the tables
# Base.prepare(engine, reflect=True)

# # Save reference to the table
# Samples = Base.classes.samples

# # Create our session (link) from Python to the DB
# session = Session(engine)


app = Flask(__name__)

from flask_sqlalchemy import SQLAlchemy

# OPTION B - Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///DataSets/belly_button_biodiversity.sqlite"

db = SQLAlchemy(app)

# OPTION B - table setup
class Samples(db.Model):
	__table_args__ = {"autoload": True, "autoload_with": db.engine}
	__tablename__ = 'samples'
    # id = db.Column(db.Integer, primary_key=True)
    # dummy_column = db.Column(db.Text)
    # __table_args__ = {'autoload': True}
   	# , 'autoload_with': engine  

class OTU(db.Model):
    __tablename__ = 'otu'

    id = db.Column(db.Integer, primary_key=True)
    otu_id = db.Column(db.Integer)
    lowest_taxonomic_unit_found = db.Column(db.String)

    def __repr__(self):
        return '<OTU %r>' % (self.name)

class MetaData(db.Model):
	__table_args__ = {"autoload": True, "autoload_with": db.engine}
	__tablename__ = 'samples_metadata'


# Create database tables
@app.before_first_request
def setup():
    # Recreate database each time for demo
    # db.drop_all()
    db.create_all()

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/names')
def names():

	# results = conn.execute(query).keys()
	# samples = [results]

	payload = {
		"data": [
			{ "name": col.name } for col in Samples.__table__.columns
		]
	}


	return jsonify(payload)


@app.route('/otu')
def otu():
	results = db.session.query(OTU.otu_id, OTU.lowest_taxonomic_unit_found).all()

	id_list = [result[0] for result in results]
	lowest_taxonomic_unit_found = [result[1] for result in results]

	plot_trace = {
		"x": id_list,
		"y": lowest_taxonomic_unit_found,
		"type": "bar"
	}

	return jsonify(plot_trace)


@app.route('/metadata/<sample>')

def metadata(sample):
	search_num = sample[3:]
	# search_num = 940

	results = db.session.query(MetaData.SAMPLEID, MetaData.AGE, MetaData.BBTYPE, MetaData.ETHNICITY, MetaData.GENDER, MetaData.LOCATION).all()

	# test_list = []

	for result in results:
		if result[0] == int(search_num):
			metadata_dict = {}
			metadata_dict["id"] = result[0]
			metadata_dict["age"] = result[1]
			metadata_dict["bb type"] = result[2]
			metadata_dict["ethnicity"] = result[3]
			metadata_dict["gender"] = result[4]
			metadata_dict["location"] = result[5]

			# test_list.append(result[0])
			return jsonify(metadata_dict)



@app.route('/wfreq/<sample>')
def washing(sample):
	search_num = sample[3:]
	results = db.session.query(MetaData.SAMPLEID, MetaData.WFREQ).all()
	for result in results:
		if result[0] == float(search_num):
			washing_dict = {"washing frequency":result[0]}
			return jsonify(washing_dict)

@app.route('/samples/<sample>')
def samples_values(sample):
	# print(sample)
	# search_num = sample[3:]
	for col in Samples.__table__.columns:
		print(col)
		if col.name == sample:
			results = db.session.query(Samples.otu_id, 'Samples.{}'.format(sample)).all()
			
			# .order_by('Samples.{}'.format(sample).desc())
			df = pd.DataFrame(results, columns=['otu_id', 'sample_value']).sort_values('sample_value', ascending=False)


			print(df)

			otu_id_list = list(df["otu_id"].astype('str'))
			sample_value_list = list(df['sample_value'].astype('str'))

			sample_value_dict = {"otu_id":otu_id_list, "sample_value":sample_value_list}

			print(type(sample_value_dict))
			# for result in results:
			# 	# print(result[1])
			# 	otu_id_list = []
			# 	values_list = []

			# 	otu_id_list.append(result[0])
			# 	values_list.append(result[1])

				# sample_value_dict = {}
				# sample_value_dict["otu ids"] = result[0]
				# sample_value_dict["sample values"] = result[1]
			return jsonify(sample_value_dict)


if __name__ == "__main__":
    app.run(debug=True)