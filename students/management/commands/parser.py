import lxml.html as html
Ronaldo_main_domain_stat = 'http://ua.tribuna.com/cristiano-ronaldo/'
page = html.parse(Ronaldo_main_domain_stat)
a = page.getroot().find_class('short-statistic').pop()
t = a.getchildren()
f= t[1].getchildren()
print f[0].text_content()

Messi_main_domain_stat = 'http://www.statbunker.com/players/getPlayerStats?player_id=18435'
page = html.parse(Messi_main_domain_stat)
a = page.getroot().find_class('genericTable table Barcelona').pop()
t = a.getchildren()
f= t[2].getchildren()
print f[3].text_content()

