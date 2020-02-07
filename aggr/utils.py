def scoretobackground(score, size="big", max_score = 100):

	if size == "big":
		low = "danger"
		medium = "warning"
		high = "success"

	if size == "small":
		low = "danger"
		medium = "warning"
		high = "success"		
	

	if score <= (max_score/3.33):
		newbg = low
			
	if score <= (max_score/1.6667) and score > (max_score/3.33):
		newbg = medium
			
	if score <= max_score and score > (max_score/1.6667):
		newbg = high
			
	return newbg	
