from mainapp import app
import pygal
from pygal.style import DarkStyle
from flask import render_template, jsonify, request, redirect
from mainapp.forms import main_search, adv_search, weapon_compare, state_compare, race_compare
from mainapp.code import query_db, get_db

@app.route('/', methods = ['GET', 'POST'])
def index():
    form = main_search()
    return render_template('index.html', form = form)

@app.route('/statistics')
def stats():

    cities = query_db("SELECT l.city, l. state, count(*) from Incident i, Location l where l.id = i.locationID group by l.city, l.state order by count(*) desc limit 10;");

    states = query_db("SELECT l.state, count(*), c.violentcrime from incident i, location l, crime c where l.id = i.locationid and l.state = c.state group by l.state order by count(*) desc limit 10;");

    title = u'How Many Cop Killings Per State'
    state_chart = pygal.Bar(height = 400, width = 1000, title = title, style = DarkStyle)
    state_names = [(state[0]) for state in states]
    killings = [(state[1]) for state in states]
    crimerate = [(float(state[2])) for state in states]
    state_chart.x_labels = state_names
    state_chart.add(u'Killing Count', killings)
    state_chart.add(u'Violent Crime Rate per 100k', crimerate)
    state_chart = state_chart.render_data_uri()

    violence = query_db("select l.state, count(*), c.violentcrime from incident i, location l, crime c where l.id = i.locationid and l.state = c.state group by l.state order by c.violentcrime desc limit 10;")
    violent_chart = pygal.Bar(height = 400, width = 1000, title = "Most Violent States", style = DarkStyle)
    state_names = [(state[0]) for state in violence]
    killings = [(state[1]) for state in violence]
    crimerate = [(float(state[2])) for state in violence]
    violent_chart.x_labels = state_names
    violent_chart.add(u'Killing Count', killings)
    violent_chart.add(u'Violent Crime Rate per 100k', crimerate)
    violent_chart = violent_chart.render_data_uri()

    races = query_db("SELECT v.race, count(*) from Incident i, Victims v where v.id = i.victimID group by v.race order by count(*) desc limit 3;")
    races_chart = pygal.Bar(width=500, title = "Most Targeted Races", style = DarkStyle)
    race_names = [(race[0]) for race in races]
    killings = [(race[1]) for race in races]
    races_chart.x_labels = race_names
    races_chart.add(u'Killing Count', killings)
    races_chart = races_chart.render_data_uri()

    agencies = query_db("SELECT i.lawenforcementagency, count(*) from Incident i group by i.lawenforcementagency order by count(*) desc limit 10;");

    weapons = query_db("SELECT i.armed, count(*) from Incident i group by i.armed order by count(*) desc limit 3;");
    weapons_chart = pygal.Bar(width = 500, title = "Top Weapons Held By Victims During Killings", style = DarkStyle)
    weapon_name = [(weapon[0]) for weapon in weapons]
    weapon_count = [(weapon[1]) for weapon in weapons]
    weapons_chart.x_labels = weapon_name
    weapons_chart.add(u'Weapon Count', weapon_count)
    weapons_chart = weapons_chart.render_data_uri()


    avg = query_db("select avg(age) as AvgAge from victims;");

    ages = query_db("select age, count(*) from victims group by age order by count(*) desc limit 10;");

    armed = query_db("SELECT (((select count(*) from Incident where armed = 'Firearm' group by armed) + (select count(*) from Incident where armed = 'Knife' group by armed) + (select count(*) from Incident where armed = 'Other' group by armed) + (select count(*) from Incident where armed = 'Vehicle' group by armed)) * 1.0 / (select count (*) from incident)) as Armed, (((select count(*) from Incident where armed = 'No') + (select count(*) from Incident where armed = 'Non-lethal firearm') + (select count(*) from Incident where armed = 'Disputed')) * 1.0 / (select count(*) from incident)) as Unarmed, ((select count(*) from Incident where armed = 'Unknown') * 1.0 / (select count(*) from incident)) as Unknown;");
    armed_chart = pygal.Pie(title='Percentage of Victims Armed or Not', style = DarkStyle)
    armed_chart.add('Armed', armed[0][0])
    armed_chart.add('Unarmed', armed[0][1])
    armed_chart.add('Unknown', armed[0][2])
    armed_chart = armed_chart.render_data_uri()

    return render_template('stats.html', weapons_chart = weapons_chart, races_chart = races_chart, violent_chart = violent_chart, armed_chart = armed_chart, state_chart = state_chart, cities = cities, races = races, agencies = agencies, weapons = weapons, avg = avg, ages = ages, armed = armed)

@app.route('/_background_process', methods = ['GET', 'POST'])
def query():
    main_query = "SELECT v.name, v.age, v.gender, v.race, i.month, i.day, i.year, l.address, l.city, l.state, i.classification, i.lawenforcementagency, i.armed from Victims v, location l, incident i where v.id = i.victimid AND l.id = i.locationid"

    query = request.args.get('query')
    by = request.args.get('by')
    if by == 'victims':
        main_query += " AND v.name LIKE ?;"
        results = query_db(main_query, ('%' + query + '%',))
    elif by == 'location':
        main_query += " AND (l.address LIKE ? OR l.city LIKE ? OR l.state LIKE ?);"
        results = query_db(main_query, ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
    return jsonify(results)

@app.route('/search', methods = ['GET', 'POST'])
def advanced():

    form = adv_search(prefix="form1")
    form.armed.choices = [(c[0], c[0]) for c in query_db("select distinct armed from incident order by armed asc;")]
    form.armed.choices.insert(0, ('armed', 'Armed'))
    form.classification.choices = [(c[0], c[0]) for c in query_db("select distinct classification from incident order by classification asc;")]
    form.classification.choices.insert(0, ('classification', 'Classification'))
    form.race.choices = [(c[0], c[0]) for c in query_db("select distinct race from victims order by race asc;")]
    form.race.choices.insert(0, ('race', 'Race'))
    form.gender.choices = [(c[0], c[0]) for c in query_db("select distinct gender from victims order by gender asc;")]
    form.gender.choices.insert(0, ('gender', 'Gender'))
    form.state.choices = [(c[0], c[0]) for c in query_db("select distinct state from location order by state asc;")]
    form.state.choices.insert(0, ('state', 'State'))

    if form.is_submitted() and form.submit.data:
        query = 'select v.name, v.age, v.gender, v.race, i.day, i.month, i.year, l.address, l.city, l.state, i.classification, i.lawenforcementagency, i.armed from victims v, incident i, location l where l.id = i.locationid and v.id = i.victimid'
        if form.armed.data != 'armed':
            query += ' AND i.armed = "%s"' % form.armed.data
        if form.classification.data != 'classification':
            query += ' AND i.classification = "%s"' % form.classification.data
        if form.race.data != 'race':
            query += ' AND v.race = "%s"' % form.race.data
        if form.gender.data != 'gender':
            query += ' AND v.gender = "%s"' % form.gender.data
        if form.state.data != 'state':
            query += ' AND l.state = "%s"' % form.state.data
        if form.min_age.data:
            query += ' AND age > %s' % form.min_age.data
        if form.max_age.data:
            query += ' AND age < %s' % form.max_age.data

        query += ';'
        victims = query_db(query)
        return render_template('results.html', victims = victims)

    weapons_form = weapon_compare(prefix="form2")
    weapons_form.weapons.choices = [(c[0], c[0]) for c in query_db("select distinct armed from incident order by armed asc;")]

    if weapons_form.is_submitted() and weapons_form.submit.data:
        if len(weapons_form.weapons.data) == 0:
            query = 'select i.armed, count(*) from incident i group by i.armed order by count(*) desc;'
            weapons = query_db(query)
            chart = pygal.Pie(title="Weapons Held By Victims", style = DarkStyle)
            for weapon in weapons:
                chart.add(weapon[0], weapon[1])

            chart = chart.render_data_uri()
            return render_template('results.html', chart = chart)

        weapons = weapons_form.weapons.data
        query = 'select i.armed, count(*) from incident i where ('
        first = True
        for weapon in weapons:
            if first:
                query += 'i.armed = "%s"' % weapon
                first = False
            else:
                query += ' OR i.armed = "%s"' % weapon

        query += ') group by i.armed order by count(*) desc;'
        weapons = query_db(query)
        chart = pygal.Bar(title = 'Weapons Held By Victims', style = DarkStyle)
        chart.x_labels = [(weapon[0]) for weapon in weapons]
        count = [(weapon[1]) for weapon in weapons]
        chart.add(u'Weapon Count', count)
        chart = chart.render_data_uri()

        return render_template('results.html', chart = chart)

    races_form = race_compare()
    races_form.race.choices = [(c[0], c[0]) for c in query_db("select distinct race from victims order by race asc;")]

    if races_form.is_submitted() and races_form.submit.data:
        if len(races_form.race.data) == 0 :
            query = 'select v.race, count(*) from Victims v, incident i where v.id = i.victimid group by v.race order by count(*) desc;'
            races = query_db(query)
            chart = pygal.Pie(title="Races Killed", style = DarkStyle)
            for race in races:
                chart.add(race[0], race[1])
            chart = chart.render_data_uri()
            return render_template('results.html', chart = chart)

        races = races_form.race.data
        query = 'select v.race, count(*) from Victims V, Incident i where v.id = i.victimID and ('
        first = True
        for race in races:
            if first:
                query += 'v.race = "%s" ' % race
                first = False
            else:
                query += 'OR v.race = "%s" ' % race

        query += ') group by v.race order by count(*) desc;'
        races = query_db(query)
        chart = pygal.Bar(title="Races Killed", style = DarkStyle)
        chart.x_labels = [(race[0]) for race in races]
        killings = [(race[1]) for race in races]
        chart.add(u'Killings', killings)
        chart = chart.render_data_uri()
        return render_template('results.html', chart = chart)

    state_form = state_compare(prefix="form3")
    state_form.states.choices = [(c[0], c[0]) for c in query_db("select distinct state from location order by state asc;")]
    if state_form.is_submitted() and state_form.submit.data:
        query = 'select c.state '
        selections = state_form.compare.data
        if selections:
            for selection in selections:
                if selection == 'count':
                    query += ', count(*) '
                    first = False
                else:
                    query += ', c.%s ' % selection
                    first = False
        else:
            query += ', count(*) '
        query += 'from crime c, incident i, location l where l.id = i.locationID AND l.state = c.state '
        states = state_form.states.data
        if states:
            query += 'AND ('
            first = True
            for state in states:
                if first:
                    query += 'c.state = "%s" ' % state
                    first = False
                else:
                    query += 'OR c.state = "%s" ' % state
            query += ')'

        sort = state_form.sort.data
        limit = state_form.limit.data
        query += ' group by c.state order by '
        if sort == 'count':
            query += 'count(*) desc limit %s;' % limit
        else:
            query += 'c.%s desc limit %s;' % (sort, limit)
        compare = query_db(query)
        chart = pygal.Bar(title = 'Comparing State Facts', style = DarkStyle)
        chart.x_labels = [(c[0]) for c in compare]
        i = 1
        for selection in selections:
            fact = [(float(c[i])) for c in compare]
            chart.add(selection, fact)
            i += 1
        chart = chart.render_data_uri()
        return render_template('results.html', chart = chart)

    return render_template('search.html', weapons_form = weapons_form, form = form, races_form = races_form, state_form = state_form)

@app.route('/results', methods = ['GET', 'POST'])
def results():
    return render_template('results.html')
