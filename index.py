#-*- coding:utf-8 -*-

from route import main
try:
	from bae.core.wsgi import WSGIApplication
	application = WSGIApplication(main.app)
except:
    main.app.run(debug=True,use_debugger=True,host='0.0.0.0',port=3000,threaded=False)
