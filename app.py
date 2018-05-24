from flask import Flask, render_template
from services.mysportsfeeds import api 

import pygal


app = Flask(__name__)

@app.route('/')
def pitch_chart():
  title = 'Pitch Chart'
  pitch_chart = pygal.XY(width=512,
                         height=512,
                         explicit_size=True,
                         #show_minor_x_labels=False,
                         #show_minor_y_labels=False,
                         inverse_y_axis=True,
                         show_x_guides=True,
                         stroke=False,
                         title=title)

  pbp = api.get_game_playbyplay(gameid='20180519-OAK-TOR', playtype='batter-up,pitch')

  for ab in pbp['gameplaybyplay']['atBats']['atBat']:
    del ab['atBatPlay'][0]

  pitches = []

  for ab in pbp['gameplaybyplay']['atBats']['atBat']:
    pitches += ab['atBatPlay']

  ball = []
  strike = []
  foul = []
  in_play = []

  strike_x_min = 256
  strike_x_max = -1
  strike_y_min = 256
  strike_y_max = -1

  # determine strike zone from called strikes
  for pitch in pitches:
    result = pitch['pitch']['result']

    x = int(pitch['pitch']['pitchedLocationX'])
    y = int(pitch['pitch']['pitchedLocationY'])

    if result == 'CALLED_STRIKE':
      strike.append((x, y))
      strike_x_min = x if x < strike_x_min else strike_x_min
      strike_x_max = x if x > strike_x_max else strike_x_max
      strike_y_min = y if y < strike_y_min else strike_y_min
      strike_y_max = y if y > strike_y_max else strike_y_max

  # approximate centre of strike zone
  zone_centre_x = int((strike_x_max + strike_x_min) / 2)
  zone_centre_y = int((strike_y_max + strike_y_min) / 2)

  ball_x_min = zone_centre_x
  ball_x_max = zone_centre_x
  ball_y_min = zone_centre_y
  ball_y_max = zone_centre_y

  for pitch in pitches:
    result = pitch['pitch']['result']

    x = int(pitch['pitch']['pitchedLocationX'])
    y = int(pitch['pitch']['pitchedLocationY'])

    if result.startswith('BALL'):
      ball.append((x, y))
    elif result.startswith('IN_PLAY'):
      in_play.append((x, y))
    elif result == 'SWINGING_STRIKE':
      strike.append((x, y))
    elif result.startswith('FOUL'):
      foul.append((x, y))

  pitch_chart.add('S', strike)
  pitch_chart.add('B', ball)
  pitch_chart.add('BIP', in_play)
  pitch_chart.add('F', foul)

  # TBD: determine strike zone from called balls

  pitch_chart.x_labels = [strike_x_min, strike_x_max]
  pitch_chart.y_labels = [strike_y_min, strike_y_max]

  return render_template('pitch_chart.html', title=title, chart=pitch_chart)
