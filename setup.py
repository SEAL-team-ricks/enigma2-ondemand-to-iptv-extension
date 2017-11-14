
from distutils.core import setup
import setup_translate

pkg = 'Extensions.RemoteChannelStreamConverter'
setup (name = 'enigma2-plugin-extensions-ondemand-to-iptv-bouquet',
	version = '1.0',
	description = 'Download programs from various ondemand services such as the BBC Iplayer, UKTV Play and ITV Player into seperate bouquets',
	packages = [pkg],
	package_dir = {pkg: 'plugin'},
	package_data = {pkg: ['locale/*/LC_MESSAGES/*.mo']},
	cmdclass = setup_translate.cmdclass, # for translation
)
