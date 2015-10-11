from subprocess import call

def generate_pdf(music, lyrics, title):
	output = '\header { title = "' + title + '"\n composer = "Lyricthon"}'
	output += '\score { << '
	output += '{ \key c \major '
	output += music
	output += ' } '

	output += '\\addlyrics {'
	output += lyrics.replace('-', '- ')
	output += ' } '

	output += '>> \layout { } \\version "2.18.2" }'

	fname = 'output.ly'
	f = open(fname, 'w')
	f.write(output)
	f.close()

	call(['/Applications/LilyPond.app/Contents/Resources/bin/lilypond', '--output=static', fname])