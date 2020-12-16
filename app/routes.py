import sys
import os
from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import CareerForm


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])

def index():

    form = CareerForm()


    form.pathway.choices = form.paths_for_career(form.career.data)


    if form.clear.data:
        return redirect('/index')
    
    if form.submit.data:

        if form.validate_on_submit():
            sys.path.append('../')
            import predict_salary as ps

            pred_wage = ps.run_model(form.pathway.data,
                                     form.state.data,
                                     form.education.data,
                                     form.experience.data)

            print(pred_wage)

            if len(pred_wage) > 1:
                form.return_data = "Without a degree your predicted wage \
                                    is $" + str(round(pred_wage[0], 2)) + \
                                    " and with a Master's Degree your predicted \
                                    wage is $" + str(round(pred_wage[1], 2)) + \
                                    "."

            else:
                form.return_data = "Your predicted wage is: $" \
                                + str(round(pred_wage[0], 2)) + ". We \
                                don't anticipate an additional degree to be \
                                helpful to you at this time."
            print("submitted")
            print(form.career.data)
            print(form.pathway.data)
            print(form.state.data)
            print(form.education.data)
            print(form.experience.data)


    if form.test_onet.data:
        print("")
        print("")
        print("Hello!")
        print("Firing up the O*Net web scraper!")
        print("Testing with a small batch of 25 job codes")
        print("")
        print("")
        print("You found data for...")

        sys.path.append('../')
        import onet_scraper
        onet_scraper.run_full_dataset("data_files/25_career_clusters.csv",
                                      "data_files/test_onet_data.csv")
        print("")
        print("All done!")
        print("Your test file has been saved to:")
        print("'project/data_files/test_onet_data.csv'")
        print("")
        print("")


    if form.test_bls.data:
        print("firing up the BLS API!")
        print("Scraping a test set of 500 job * state wage observations...")

        import bls_parser
        bls_parser.test()

        print("")
        print("All done!")
        print("")
        print("")

    if form.test_educ.data:
        print("")
        print("")
        print("")
        print("Our code for education data lives in the")
        print("school_tuition.py file.")
        print("")
        print("Unfortunately due to the dynamic nature of the USnews website,")
        print("our source, it once worked, but no longer does. T_T")
        print("")
        print("The data collected lives in data_files under:")
        print("1. best_law_schools.csv")
        print("2. best_engineering_school.csv")
        print("3. best_business_school.csv")
        print("")
        print("")
        print("")

    return render_template('index.html', form=form)
