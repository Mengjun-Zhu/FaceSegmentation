import os
import cv2
import numpy as np
import matplotlib.pyplot as plt


def face_cluster(imgPath, imgFilename, savedImgPath, savedImgFilename, k):
   """
   parameters:
   imgPath: the path of the image folder. Please use relative path
   imgFilename: the name of the image file
   savedImgPath: the path of the folder you will save the image
   savedImgFilename: the name of the output image
   k: the number of clusters of the k-means function
   function: using k-means to segment the image and save the result to an image with a bounding box
   """
   #Use Opencv to load the image.
   img_filePath = os.path.join(imgPath, imgFilename)
   img_BGR = cv2.imread(img_filePath)
   img_RGB = cv2.cvtColor(img_BGR, cv2.COLOR_BGR2RGB)  # Opencv uses BGR hence we convert it to RGB.
   height, width, channel = img_RGB.shape

   pixel_data = img_RGB.reshape((-1, 3))
   pixel_data = np.float32(pixel_data)

   criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 500, 0.1)
   _, label, center = cv2.kmeans(pixel_data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
   center = np.uint8(center)

   #Now we use img_segmented to storage the segmentation image generated by our kmeans result.
   img_segmented = center[label.flatten()]
   img_segmented = img_segmented.reshape(img_RGB.shape)

   '''
   The following for loop is used to obtain the face cluster.
   The following link provides a reference for the skin color.
   https://colorswall.com/palette/2513 
   we could obtain that the skin color of a white people is approximately in
   the range of three colors: #c58c85{rgb(197, 140, 133)}, #ecbcb4{rgb(236, 188, 180)}, #d1a3a4{rgb(209, 163, 164)}.
   Hence if a center of a cluster is in this range, we could assert that it is the face cluster.
   '''
   for i in range(k):
       if (197 <= center[i][0] <= 236) & (140 <= center[i][1] <= 188) & (133 <= center[i][2] <= 180):
           face_cluster_num = i
           break

   # Now we create a binary image with the same size of our original image.
   # We set this image white(255) where we meet the face cluster and the remaining part black(0).
   img_binary = np.zeros(height * width)
   img_binary[label.flatten() == face_cluster_num] = 255
   img_binary = img_binary.reshape(height, width)

   # Some noise might be added to the face cluster since kmeans is unsupervised.
   # Hence we apply the Guassian filter to revise the noise.
   img_binary_filtered = cv2.GaussianBlur(img_binary, (3, 3), 0)

   '''
   Now we need to find the location of the face cluster using the binary image.
   We use a ndarray face_location to record the location of the face cluster.
   By running the following for loop, when one of the pixels in the binary image equals to 1, 
   we could assert that this pixel is in the face cluster.
   Hence by recording those "1"s, we obtain the location of the face clusters.
   '''
   face_location = []
   for i in range(height):
       for j in range(width):
           if img_binary_filtered[i][j] == 255:
               face_location.append([i, j])
   face_location = np.array(face_location)
   face_location = face_location.reshape(2, face_location.shape[0])

   '''
   By deriving the maximum and minimum of the x,y coordinates of face_location respectively, 
   we hence find a rectangular boundary.
   Now we could draw our bounding box based on this rectangular boundary.
   '''
   y_min, x_min = face_location.min(axis=1)
   y_max, x_max = face_location.max(axis=1)
   img_bounding_box = cv2.rectangle(img_BGR, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)

   img_savedPath = os.path.join(savedImgPath, savedImgFilename)
   cv2.imwrite(img_savedPath, img_bounding_box)

   # return the binary image.
   return img_binary_filtered

if __name__ == '__main__':
   imgPath = "image"
   imgFilename = "face_d2.jpg"
   savedImgPath = r"image"
   savedImgFilename = "face_d2_face.jpg"
   k = 8
   image_binary = face_cluster(imgPath, imgFilename, savedImgPath, savedImgFilename, k)

   #plot the binary image
   plt.figure(1)
   plt.imshow(image_binary, cmap="gray")
   plt.show()

