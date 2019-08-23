import cv2
import numpy as np

class Growth:
    def __init__(self):
        self.img = np.zeros(shape=(64,64,1)).astype('float32')
        # self.img = np.random.uniform(size=(64,64,1)).astype('float32')
        print(self.img.shape)
        self.imgh = self.img.shape[0]
        self.imgw = self.img.shape[1]

        # build field estimation kernel
        # use Coulomb's law
        # f = kq1q2/r^2
        # f = 1/r^2, cap @ 10

        x = np.linspace(-1,1,55)
        y = np.linspace(-1,1,55)
        xv, yv = np.meshgrid(x, y)

        dist_sq = xv**2 + yv**2

        self.kernel_x = 
        # min:0.001/1 = 0.001
        # max:0.001/0.00001 = 100
        self.kernel = (0.001/(xv**2 + yv**2 + 0.00001) - 0.0015 )/100

    def step(self):
        img = self.img

        # 1. accumulate potential
        img[self.imgh//2,self.imgw//2] += 10.0

        # # 2. calculate field strenth
        # fs = cv2.GaussianBlur(img,(11,11),0)
        fs = cv2.filter2D(img,-1,self.kernel)
        cv2.imshow('field',np.power(fs, .2))

        # 3. calculate field gradient (along the gradient you grow)
        sobelx = cv2.Sobel(img,cv2.CV_32F,1,0,ksize=1)
        sobely = cv2.Sobel(img,cv2.CV_32F,0,1,ksize=1)
        cv2.imshow('sobelx',sobelx+0.5)

        # 4. for each pixel, grow yourself along the gradient.

        def shift(grad): # grad should be 0-centered
            grad = np.random.normal(loc=0, scale=.5) - grad
            return int(grad)

        def cap(x,k):
            if x<0: return 0
            if x>=k: return k-1
            return x

        # newimg = img*0.
        for row in range(img.shape[0]):
            for col in range(img.shape[1]):
                potential = img[row,col] * 0.1
                gradx = sobelx[row,col]
                grady = sobely[row,col]

                # choose shift value given gradient
                shiftx = shift(gradx)
                shifty = shift(grady)

                img[cap(row+shifty,self.imgh),cap(col+shiftx,self.imgw)] += potential
                img[row,col] -= potential

        # 5. blend in
        # factor = np.random.uniform(size=self.img.shape).astype('float32')
        # factor=0.5
        # self.img = newimg * (1-factor) + self.img * factor
        cv2.imshow('haha',np.power(self.img, .2))


g = Growth()
for i in range(1000):
    g.step()
    k = cv2.waitKey(50)
    if k>0 :break
