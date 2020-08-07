import cv2
import numpy as np
import time
from skimage.measure import compare_ssim as ssim
import astarsearch
import traversal
def main(image_filename):
	occupied_grids = []
	planned_path = {}
	image = cv2.imread(image_filename)
	(winW, winH) = (60, 60)
	obstacles = []
	index = [1,1]
	blank_image = np.zeros((60,60,3), np.uint8)
	list_images = [[blank_image for i in xrange(10)] for i in xrange(10)]
	maze = [[0 for i in xrange(10)] for i in xrange(10)]
	for (x, y, window) in traversal.sliding_window(image, stepSize=60, windowSize=(winW, winH)):
		if window.shape[0] != winH or window.shape[1] != winW:
			continue
		clone = image.copy()
		cv2.rectangle(clone, (x, y), (x + winW, y + winH), (0, 255, 0), 2)
		crop_img = image[x:x + winW, y:y + winH]
		list_images[index[0]-1][index[1]-1] = crop_img.copy()
		average_color_per_row = np.average(crop_img, axis=0)
		average_color = np.average(average_color_per_row, axis=0)
		average_color = np.uint8(average_color)
		if (any(i <= 240 for i in average_color)):
			maze[index[1]-1][index[0]-1] = 1
			occupied_grids.append(tuple(index))
		if (any(i <= 20 for i in average_color)):
			obstacles.append(tuple(index))
		cv2.imshow("Window", clone)
		cv2.waitKey(1)
		time.sleep(0.025)
		index[1] = index[1] + 1
		if(index[1]>10):
			index[0] = index[0] + 1
			index[1] = 1
	list_colored_grids = [n for n in occupied_grids if n not in obstacles]
	for startimage in list_colored_grids:
		key_startimage = startimage
		img1 = list_images[startimage[0]-1][startimage[1]-1]
		for grid in [n for n in list_colored_grids  if n != startimage]:
			img = 	list_images[grid[0]-1][grid[1]-1]
			image = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
			image2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			s = ssim(image, image2)
			if s > 0.9:
				result = astarsearch.astar(maze,(startimage[0]-1,startimage[1]-1),(grid[0]-1,grid[1]-1))
				list2=[]
				for t in result:
					x,y = t[0],t[1]
					list2.append(tuple((x+1,y+1)))
					result = list(list2[1:-1])
				if not result:
					planned_path[startimage] = list(["NO PATH",[], 0])
				planned_path[startimage] = list([str(grid),result,len(result)+1])

	for obj in list_colored_grids:
		if not(planned_path.has_key(obj)):
			planned_path[obj] = list(["NO MATCH",[],0])

	return occupied_grids, planned_path
if __name__ == '__main__':
    image_filename = "test_images/test_image3.jpg"
    main(image_filename)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
