from django.shortcuts import render_to_response

import json

#def wn(request):
#	print '>>> ', request.method
#	#print '>>> ',request.raw_post_data
#	#print '>>> ',request.body
#	#print '>>> ', request.read()
#
#	print
#	if request.method == "GET":
#		print '>>> ',request.body
#		#print dir(request.GET)
#
#	if request.method == "PUT":
#		print '>>> ',request.body
#		print '>>> ', json.loads(request.body)
#		#print dir(request)
#
#	if request.method == "POST":
#		print '>>> ',request.body
#		#print '>>> ', json.loads(request.body)
#		#print dir(request)
#		print request.POST.get('foo1')
#	print
#
#	return render_to_response('void.html')



def wn(request):
	print '>>> ', request.method

	if request.method == "GET":
		print '>>> ', request.body

	if request.method == "PUT":
		print '>>> ', request.body
		print '>>> ', json.loads(request.body)

	if request.method == "POST":
		print '>>> ', request.body
		print '>>> ', request.POST.get('foo1')
	print

	return render_to_response('void.html')



