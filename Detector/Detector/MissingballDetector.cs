using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.IO;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Drawing;
using System.Drawing.Imaging;
using GxSingleCam;
using System.Windows.Forms;
using AForge.Imaging;
using AForge.Imaging.Filters;


namespace MissingballProject
{
    public class MissingballDetector
    {

        string str_SingleShotPicName = "inspect.bmp";
        public bool[] flags = new bool[] { true, true, true };
        public int leftEnd = 0;
        public int rightEnd = 0;
        public int upperBound = 0;
        public int buttumBound = 0;
        public int blb = 0;
        public double ratio = 1;

        public bool Detect()
        {
            AcquireImage();
            return Detecting(str_SingleShotPicName);
        }
        public bool Detect(string imagename)
        {
            return Detecting(imagename);
        }

        bool Detecting(string imagename)
        {
            Bitmap bmpProc = new Bitmap(imagename);
            MessageBox.Show("Image read");
            //imShow(bmpProc);
            double[,,] hsv = rgb2hsv(bmpProc);

            int[] blueIndex = detectBlue(hsv);
            Bitmap gray = getGray(bmpProc);
            MessageBox.Show("Get gray image");
            //imShow(gray);
            Bitmap binary = thresholdImg(gray, 250);
            MessageBox.Show("Get binary image");

            Bitmap gradient = gradientImg(binary);
            MessageBox.Show("Get gradient image");

            //imShow(gradient);
            //MessageBox.Show("Threshold the image");
            //imShow(binary);
            Bitmap canny = CannyEdge(gradient);
            MessageBox.Show("Canny edge detector");

            Bitmap contour = getContour(canny);
            MessageBox.Show("Get contour");

            Bitmap resized = resizeImg(contour, upperBound, buttumBound, leftEnd, rightEnd);
            ratio = getRatio(rightEnd - leftEnd, buttumBound - upperBound);
            Console.WriteLine(buttumBound - upperBound);
            Console.WriteLine(rightEnd - leftEnd);
            p1(blueIndex, upperBound, blb);
            p2(contour, 10);
            p3(gray, 40);
            //Console.WriteLine(ratio);
            //Console.WriteLine(contour.Width);
            //Console.WriteLine(resized.Width);
            //imShow(resized);
            Console.WriteLine(flags[0]);
            Console.WriteLine(flags[1]);
            Console.WriteLine(flags[2]);


            return true;
        }

        double[,,] rgb2hsv(Bitmap rgbImg)
        {
            double[,,] hsvImg = new double[rgbImg.Height, rgbImg.Width, 3];
            for (int x = 0; x < rgbImg.Width; x++)
            {
                for (int y = 0; y < rgbImg.Height; y++)
                {
                    Color color = rgbImg.GetPixel(x, y);
                    //Console.WriteLine(color.R);
                    //Console.WriteLine(color.G);
                    //Console.WriteLine(color.B);
                    //imShow(rgbImg);
                    int max = Math.Max(color.R, Math.Max(color.G, color.B));
                    int min = Math.Min(color.R, Math.Min(color.G, color.B));
                    //hue, saturation, value
                    hsvImg[y, x, 0] = color.GetHue() / 360 * 256;
                    //Console.WriteLine(color.GetHue());
                    hsvImg[y, x, 1] = (max == 0) ? 0 : (1d - (1d * min / max)) * 256;
                    //Console.WriteLine(hsvImg[y, x, 1]);
                    hsvImg[y, x, 2] = max;
                    //Console.WriteLine(hsvImg[y, x, 1]);

                }
            }
            return hsvImg;
        }

        Bitmap getGray(Bitmap rgbImg)
        {
            Bitmap grayImg = new Bitmap(rgbImg);
            for (int y = 0; y < rgbImg.Height; y++)
            {
                for (int x = 0; x < rgbImg.Width; x++)
                {
                    Color color = rgbImg.GetPixel(x, y);
                    int avg = (color.R + color.G + color.B) / 3;
                    grayImg.SetPixel(x, y, Color.FromArgb(255, avg, avg, avg));
                }
            }
            return grayImg;
        }

        void imShow(Bitmap img)
        {
            Form f = new Form();
            f.Controls.Add(new PictureBox() { Image = img, Dock = DockStyle.Fill });
            f.ShowDialog();
        }

        Bitmap thresholdImg(Bitmap gray, double threshold)
        {
            Bitmap binary = new Bitmap(gray);
            for (int y = 0; y < gray.Height; y++)
            {
                for (int x = 0; x < gray.Width; x++)
                {
                    Color intensity = gray.GetPixel(x, y);
                    Color newIntensity = intensity.B < threshold ? Color.FromArgb(intensity.A, 255, 255, 255) : Color.FromArgb(intensity.A, 0, 0, 0);
                    binary.SetPixel(x, y, newIntensity);
                }
            }
            return binary;
        }

        void AcquireImage()
        {
            try
            {
                Camera objCamera = new Camera();
                objCamera.SingleShot(str_SingleShotPicName);
                objCamera = null;
                return;
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        Bitmap CannyEdge(Bitmap bmp)
        {
            Bitmap tmp = AForge.Imaging.Image.Clone(bmp, bmp.PixelFormat);
            //higherThreshold default = 100 lower default = 20
            CannyEdgeDetector obj_canny = new CannyEdgeDetector(150, 10);
            Bitmap cannyEdges = obj_canny.Apply(tmp.PixelFormat != PixelFormat.Format8bppIndexed ? Grayscale.CommonAlgorithms.BT709.Apply(tmp) : tmp);
            return cannyEdges;
        }

        Bitmap gradientImg(Bitmap gray)
        {
            Bitmap gra = new Bitmap(gray);
            for (int y = 1; y < gray.Height - 1; y++)
            {
                for (int x = 1; x < gray.Width - 1; x++)
                {
                    int intensX = Math.Abs(gray.GetPixel(x - 1, y).B - gray.GetPixel(x + 1, y).B);
                    int intensY = Math.Abs(gray.GetPixel(x, y - 1).B - gray.GetPixel(x, y + 1).B);
                    int newIntens = (intensX + intensY) / 2;
                    gra.SetPixel(x, y, Color.FromArgb(255, newIntens, newIntens, newIntens));
                }
            }
            return gra;
        }

        Bitmap getContour(Bitmap gradient)
        {
            //Bitmap tmp = new Bitmap(1,1);
            //tmp.SetPixel(0, 0, Color.White);
            Bitmap contour = new Bitmap(gradient.Width, gradient.Height);
            leftEnd = (int)gradient.Width / 2;
            rightEnd = (int)gradient.Width / 2;
            buttumBound = (int)gradient.Height / 2;

            for (int y = 0; y < gradient.Height; y++)
            {
                for (int x = 0; x < gradient.Width; x++)
                {
                    if (gradient.GetPixel(x, y).B > 0)
                    {
                        contour.SetPixel(x, y, Color.FromArgb(255, 0, 0, 0));
                        leftEnd = (x < leftEnd) ? x : leftEnd;
                        buttumBound = (y > buttumBound) ? y : buttumBound;
                        break;
                    }

                }
            }
            for (int y = gradient.Height - 1; y >= 0; y--)
            {
                for (int x = gradient.Width - 1; x >= 0; x--)
                {
                    if (gradient.GetPixel(x, y).B > 0)
                    {
                        contour.SetPixel(x, y, Color.FromArgb(255, 0, 0, 0));
                        rightEnd = (x > rightEnd) ? x : rightEnd;
                        buttumBound = (y > buttumBound) ? y : buttumBound;
                        break;
                    }

                }
            }
            for (int y = 0; y < contour.Height; y++)
            {
                for (int x = 0; x < contour.Width; x++)
                {
                    if (contour.GetPixel(x, y) == Color.FromArgb(255, 0, 0, 0))
                    {
                        contour.SetPixel(x, y, Color.FromArgb(255, 255, 255, 255));
                    }
                    else
                    {
                        contour.SetPixel(x, y, Color.FromArgb(255, 0, 0, 0));
                    }
                }
            }

            return contour;
        }

        Bitmap resizeImg(Bitmap img, int upper, int lower, int left, int right)
        {
            int width = right - left;
            int height = lower - upper;
            Bitmap resized = new Bitmap(width, height);
            for (int x = 0; x < width; x++)
            {
                for (int y = 0; y < height; y++)
                {
                    Color color = img.GetPixel(left + x, upper + y);
                    resized.SetPixel(x, y, color);
                }
            }
            return resized;
        }

        int[] detectBlue(double[,,] hsv)
        {
            bool upperFound = false;
            Bitmap blue = new Bitmap(hsv.GetLength(1), hsv.GetLength(0));
            int[] index = new int[hsv.GetLength(0)];

            for (int row = 0; row < hsv.GetLength(0); row++)
            {
                for (int col = 0; col < hsv.GetLength(1); col++)
                {
                    double h = hsv[row, col, 0];
                    double s = hsv[row, col, 1];
                    double v = hsv[row, col, 2];

                    if (h > 100 && h < 180 && s > 60 && s < 255 && v > 46 && v < 255)
                    {
                        blue.SetPixel(col, row, Color.White);
                        index[row] += 1;
                    }
                    else
                    {
                        blue.SetPixel(col, row, Color.Black);
                    }
                }
            }
            //imShow(blue);
            for (int i = 0; i < hsv.GetLength(0) - 1; i++)
            {
                if (index[i] > 60 && index[i + 1] > 60 && !upperFound)
                {
                    upperBound = i;
                    upperFound = true;
                }
                if (upperFound && index[i] < 60 && index[i + 1] < 60)
                {
                    blb = i;
                    break;
                }
            }
            //imShow(blue);
            return index;
        }

        double getRatio(int width, int height)
        {
            return ((double)height / width);
        }

        int[] SubArray(int[] data, int index, int length)
        {
            int[] result = new int[length];
            Array.Copy(data, index, result, 0, length);
            return result;
        }

        void p1(int[] index, int upper, int lower)
        {
            int length = lower - upper;
            int[] subArray = SubArray(index, upper, length);
            int max = subArray.Max();
            Console.WriteLine(max);
            int maxIndex = subArray.ToList().IndexOf(max);
            Console.WriteLine(maxIndex);
            flags[0] = (maxIndex > 0.6 * length);
        }

        void p3(Bitmap gray, int threshold)
        {
            int length = buttumBound - upperBound;
            int width = rightEnd - leftEnd;
            int p3f = 0;
            Bitmap threshed = thresholdImg(gray, threshold);
            threshed = resizeImg(threshed, upperBound, buttumBound, leftEnd, rightEnd);
            int[] intensIndex = new int[threshed.Height];
            for (int row = (int)length / 2; row < length; row++)
            {
                for (int col = 0; col < width; col++)
                {
                    intensIndex[row] += (threshed.GetPixel(col, row).B > 0) ? 1 : 0;
                }
                //Console.WriteLine(intensIndex[row]);
                p3f += (intensIndex[row] > 90) ? 1 : 0;
            }
            flags[2] = (p3f > 3);
            imShow(threshed);
        }

        void p2(Bitmap edge, int threshold)
        {
            Bitmap edged = resizeImg(edge, upperBound, buttumBound, leftEnd, rightEnd);
            imShow(edged);
            Bitmap resized = resizeImg(edge, blb - 3, blb + 12, leftEnd, rightEnd);
            imShow(resized);
            int left = 0;
            int right = 0;
            for (int col = 0; col < resized.Width; col++)
            {
                if (left != 0)
                {
                    break;
                }
                for (int row = 0; row < resized.Height; row++)
                {
                    if (resized.GetPixel(col, row).B > 0)
                    {
                        left = col;
                        break;
                    }
                }
            }
            for (int col = (int)resized.Width / 2; col > 0; col--)
            {
                if (right != 0)
                {
                    break;
                }
                for (int row = 0; row < resized.Height; row++)
                {

                    if (resized.GetPixel(col, row).B > 0)
                    {
                        right = col;
                        break;
                    }
                }
            }
            flags[1] = ((right - left) < threshold);
            Console.WriteLine(right - left);
        }
    }
}
