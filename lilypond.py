from subprocess import call
import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read('config.ini')
lilypond_path = Config.get('General', 'LilypondPath')

def generate_pdf(music, lyrics, title):
	output = '\header { title = "' + title + '"\n composer = "Lyricthon"}'
	output += '\score { << '
	output += '{ \key c \major '
	output += music
	output += ' } '

	output += '\\addlyrics {'
	output += lyrics.replace('-', '- ')
	output += ' } '

	output += '>> \layout { } }'

	fname = 'output.ly'
	f = open(fname, 'w')
	f.write(output)
	f.close()

	call([lilypond_path, '--output=static', fname])