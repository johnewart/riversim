package nij.qrfrp.experimental;


import java.awt.Point;
import java.awt.image.BufferedImage;
import java.awt.image.Raster;
import java.awt.image.WritableRaster;
import java.io.File;
import java.io.IOException;
import java.util.HashSet;
import java.util.Iterator;

import javax.imageio.ImageIO;

import nij.qrfrp.util.ImageUtil;


/**
 * <p> Class that thins a binarized image using the Hilditch method.
 * This iterative process that goes through each edge pixel in the image and 
 * marks pixels which satisfy Hilditch's 6 conditions (see resources below for specifics).
 * Once every pixel is examined, those that were marked are turned to black.
 * The process continues until an iteration occurs during which no pixels are
 * marked. </p>
 * 
 * <p>For more information see 
 * <a href="http://cgm.cs.mcgill.ca/~godfried/teaching/projects97/azar/skeleton.html"> 
 * "Hilditch's Algorithm for Skeletonization" by Danielle Azar</a> or <a href="http://www.citr.auckland.ac.nz/techreports/2002/CITR-TR-112.pdf">"Skeletons in Digital Image Processing" 
 * by Gisela Klette</a>.</p>  
 * 
 * <p><b>NOTE:</b>  D. Azar states that there are two patterns that get erased by the Hilditch algorithm, but
 * the this class was implemented based on the content of the G. Klette paper (which makes no mention
 * of these patterns).</p>   
 * 
 * <p>This software is distributed under the GNU General Public License, version 3.0.
 * A copy of the license should have been distributed along with the code. If not, 
 * please visit http://www.fsf.org to view the terms of the license.</p>
 * 
 * @author jmetzger 
 */
public class Hilditch 
{
	final private static boolean DEBUG = false; 
	
	private BufferedImage inputImage;
	private int[][] edgeData; 
	private int[][] markedPixels;
	private BufferedImage outputImage;
		
	/**
	 * <p>Constructor: create a Hilditch object and initialize the image to be thinned.
	 * This class treats all non-zero pixels as edge points and all pixels with a value of 
	 * 0 as background pixels.</p>  
	 * 
	 * @param inputImage the image to be thinned
	 */
	public Hilditch(BufferedImage inputImage)
	{
		if(inputImage.getData().getNumBands()>1)
			inputImage = ImageUtil.convertRGBToGray(inputImage);
		this.inputImage = inputImage;	
		this.edgeData = new int[inputImage.getWidth()][inputImage.getHeight()];
		loadEdgeData(inputImage);
		this.markedPixels = new int[inputImage.getWidth()][inputImage.getHeight()];
		clearMarkedPixelArray();
		this.outputImage = new BufferedImage(inputImage.getWidth(), inputImage.getHeight(), inputImage.getType());
	}
	
	/**
	 * <p>Loads the input image into a 2D double array, the elements of which are either
	 * 0 (background) or 1 (object to be thinned).  Non-zero pixel values in the edge image
	 * are treated as object pixels and set to 1 in the 2D array.</p>  
	 * 
	 * @param edgeImage the image to be loaded
	 */
	private void loadEdgeData(BufferedImage edgeImage)
	{			
		Raster edgeRaster = edgeImage.getData();
		
		for(int i = 0; i<edgeImage.getHeight(); i++)
		{
			for(int j = 0; j<edgeImage.getWidth(); j++)
			{
				edgeData[j][i] = edgeRaster.getSample(j,i,0) == 0 ? 0 : 1; 
			}
		}
	}
	
	
	/**
	 * <p>Clears the array of pixels marked for deletion.</p> 
	 */
	private void clearMarkedPixelArray()
	{
		for(int i = 0; i<inputImage.getHeight(); i++)
		{
			for(int j = 0; j<inputImage.getWidth(); j++)
			{
				markedPixels[j][i] = 0;
			}
		}
	}
	
	/**
	 * <p>Performs the thinning without saving diagnostic images.</p>  
	 * @return the thinned image
	 */
	public BufferedImage thin() {
		return thin(null);
	}
	
	/**
	 * Thins the image until we reach an iteration during which no pixels are 
	 * marked.   
	 * 
	 * @param diagnosticDir the directory to save diagnostic images to 
	 * @return the thinned image
	 */
	public BufferedImage thin(File diagnosticDir)
	{
		//if a diagnostic directory is specified, we want to create it
		if (diagnosticDir!=null) {
			//if we can't create the directory, we set the file to null so we don't try to save there
			if(!diagnosticDir.mkdirs())
				diagnosticDir = null;
		}
		outputImage = ImageUtil.createCopy(inputImage);
		WritableRaster outputRaster = outputImage.getRaster();		
		HashSet<Point> newBackgroundPoints  = this.singleIteration();
		int counter = 0;
		do
		{	
			Iterator<Point> newPointIterator = newBackgroundPoints.iterator();
			if(DEBUG) System.out.println("Number of points to be marked as background: "+newBackgroundPoints.size());
			while(newPointIterator.hasNext())
			{
				Point tempPoint = newPointIterator.next();
				outputRaster.setSample(tempPoint.x, tempPoint.y, 0, 0);
			}			
			
			//reset markedPoints and edge data;
			loadEdgeData(outputImage);
			clearMarkedPixelArray();
			newBackgroundPoints = this.singleIteration();	
			if (diagnosticDir!=null) {				
				try {
					ImageIO.write(outputImage, "bmp", new File(diagnosticDir+File.separator+counter+".bmp"));
				} catch (IOException e) {
					// Auto-generated catch block
					e.printStackTrace();
				} catch (NullPointerException e) {
					e.printStackTrace();
				}
			}
			counter++;
			
		}while(newBackgroundPoints.size()>0);
							
		return outputImage;
	}
	
	/**
	 * <p>Performs a single iteration of the Hilditch algorithm and returns points that are
	 * marked for deletion.  Each pixel in the image is examined to see if each 
	 * pixel-of-interest meets Hilditch's criteria for deletion.  Pixels that meet the criteria
	 * are added to a set of points for deletion.  </p>
	 * 
	 * @return a HashSet of Point values represting pixels marked for deletion
	 */
	private HashSet<Point> singleIteration()
	{	
		HashSet<Point> markedPoints = new HashSet<Point>();
		for(int i = 1; i<inputImage.getHeight()-1; i++)
		{
			for(int j = 1; j<inputImage.getWidth()-1; j++)
			{
				int[] pixelNeighborhood = getPixelNeighborhood(j, i);
				int[] markedNeighborhood = getMarkedPixelNeighborhood(j, i);
				int currentPixel = edgeData[j][i];
												
				boolean a1 = (currentPixel == 1);				
				boolean a2 = (calculateNumberOfZeroNeighbors(pixelNeighborhood)>=1);
				boolean a3 = (calculateNumberOfNonZeroNeighbors(pixelNeighborhood)>1);
				boolean a4 = (calculateNumberOfUnmarkedNeighbors(markedNeighborhood)>=1);				
				boolean a5 = (calculateHCrossingNumber(pixelNeighborhood)==1);
				boolean a6 = true;				
				if(markedNeighborhood[2]==1) 
				{
					
					int[] tempNeighborhood = getPixelNeighborhood(j,i);
					tempNeighborhood[2] = 0;
					a6 = (calculateHCrossingNumber(tempNeighborhood) == 1);
				}				
				boolean a7 = true;
				if(markedNeighborhood[4]==1) 
				{
					int[] tempNeighborhood = getPixelNeighborhood(j,i);
					tempNeighborhood[4] = 0;
					a7 = (calculateHCrossingNumber(tempNeighborhood) == 1);
				}
				
				if(a1&&a2&&a3&&a4&&a5&&a6&&a7) 
				{
					markedPixels[j][i] = 1;					
					markedPoints.add(new Point(j,i));
				}
			}
		}
			
		return markedPoints;
	}
	
	/**
	 * <p>Obtain the pixels surrounding the current pixel in an int[] with indices as follows:</p>
	 * 
	 * <p><code>[ 3 ][ 2 ][ 1 ]</code></p>
	 * <p><code>[ 4 ][ P ][ 0 ]</code></p>
	 * <p><code>[ 5 ][ 6 ][ 7 ]</code></p> 
	 * 
	 * @param x current pixel's x-coordinate
	 * @param y current pixel's y-coordinate
	 * @return an int[] containing the current pixel's neighbors as shown in the figure above
	 */
	private int[] getPixelNeighborhood(int x, int y)
	{
		int[] surroundingPixels = new int[8];

		surroundingPixels[0] = edgeData[x+1][y];
		surroundingPixels[1] = edgeData[x+1][y-1];
		surroundingPixels[2] = edgeData[x][y-1];
		surroundingPixels[3] = edgeData[x-1][y-1];
		surroundingPixels[4] = edgeData[x-1][y];
		surroundingPixels[5] = edgeData[x-1][y+1];
		surroundingPixels[6] = edgeData[x][y+1];
		surroundingPixels[7] = edgeData[x+1][y+1];
		
		return surroundingPixels;
	}
	
	/**
	 * <p>Obtain the marked pixels surrounding the current pixel in an int[] with indices as follows:</p>
	 * 
	 * <p><code>[ 3 ][ 2 ][ 1 ]</code></p>
	 * <p><code>[ 4 ][ P ][ 0 ]</code></p>
	 * <p><code>[ 5 ][ 6 ][ 7 ]</code></p> 
	 * 
	 * @param x current pixel's x-coordinate
	 * @param y current pixel's y-coordinate
	 * @return an int[] containing the current pixel's marked neighbors as shown in the figure above
	 */
	private int[] getMarkedPixelNeighborhood(int x, int y)
	{
		int[] surroundingMarkedPixels = new int[8];

		surroundingMarkedPixels[0] = markedPixels[x+1][y];
		surroundingMarkedPixels[1] = markedPixels[x+1][y-1];
		surroundingMarkedPixels[2] = markedPixels[x][y-1];
		surroundingMarkedPixels[3] = markedPixels[x-1][y-1];
		surroundingMarkedPixels[4] = markedPixels[x-1][y];
		surroundingMarkedPixels[5] = markedPixels[x-1][y+1];
		surroundingMarkedPixels[6] = markedPixels[x][y+1];
		surroundingMarkedPixels[7] = markedPixels[x+1][y+1];
		
		return surroundingMarkedPixels;		
	}
	
	/**
	 * <p>Calculates the number of marked neighbors given an array of pixels.</p>
	 *  
	 * @param surroundingMarkedPixels an array of pixel values
	 * @return the number of marked neighbors
	 */
	private int calculateNumberOfMarkedNeighbors(int[] surroundingMarkedPixels)
	{
		int markedPixels = 0;
		for(int i = 0; i<8; i++)
		{
			if(surroundingMarkedPixels[i]==1)
				markedPixels++;			
		}
				
		return markedPixels;
	}
	
	/**
	 * <p>Calculates the number of non-marked neighbors given an array of pixels.</p>
	 * 
	 * @param surroundingMarkedPixels an array of pixel values
	 * @return the number of unmarked neighbors
	 */
	private int calculateNumberOfUnmarkedNeighbors(int[] surroundingMarkedPixels)
	{
		return (8 - calculateNumberOfMarkedNeighbors(surroundingMarkedPixels));
	}
	
	
	/**
	 * <p>Calculates the H-crossing number.  This value represents the number of distinct 
	 * 0-component object points and is used in Hilditch's conditions for deletion.</p>  
	 * 
	 * @param surroundingPixels an array of pixel values
	 * @return the H-crossing number
	 */
	private int calculateHCrossingNumber(int[] surroundingPixels)
	{		
		int hCrossingNumber = 0;
		
		for(int i = 0; i<4; i++)
		{			
			int tempP1 = surroundingPixels[i*2];
			int tempP2 = surroundingPixels[i*2+1];
			int tempP3 = (i*2+2)==8 ? surroundingPixels[0] : surroundingPixels[i*2+2];
			hCrossingNumber += tempP1==0 && (tempP2==1 || tempP3 == 1) ? 1 : 0;
			if(DEBUG) System.out.println("H-crossing number after processing [" + (i*2) + "] = " + hCrossingNumber);
		}		
		if(DEBUG) System.out.println();
		
		return hCrossingNumber;
	}
	
	/**
	 * <p>Calculates the number of non-zero neighbors surrounding a pixel.</p>
	 * 
	 * @param surroundingPixels an array of pixel values
	 * @return the number of non-zero neighbors
	 */
	private int calculateNumberOfNonZeroNeighbors(int[] surroundingPixels)
	{
		int nonZeroNeighbors = 0;
		
		for(int i = 0; i<8; i++)
		{
			nonZeroNeighbors += surroundingPixels[i]==0 ? 0 : 1;  
		}
		return nonZeroNeighbors;
	}
	
	/**
	 * <p>Calculates the number of zero neighbors surrounding a pixel.</p>
	 *  
	 * @param surroundingPixels an array of pixel values
	 * @return the number of neighbors with a value of 0
	 */
	private int calculateNumberOfZeroNeighbors(int[] surroundingPixels)
	{
		return (8 - calculateNumberOfNonZeroNeighbors(surroundingPixels));
	}
	
//	/**
//	 * <p>Calculates the R-crossing number for a group of pixels.  This value / 2 corresponds to the 
//	 * number of distinct 1-component object points in the group of pixels.</p>
//	 * 
//	 * <p>The R-crossing value is of use in other thinning algorithms, but not used for 
//	 * Hilditch.</p>
//	 *  
//	 * @param surroundingPixels an array of pixel values 
//	 * @return the R-crossing value
//	 */
//	private int calculateRCrossingNumber(int[] surroundingPixels)
//	{
//		int rCrossingNumber = 0;
//		
//		for(int i = 0; i<8; i++)
//		{
//			int tempP1 = surroundingPixels[i];
//			int tempP2 = i == 7 ? surroundingPixels[0] : surroundingPixels[i+1];
//			int diff = tempP2 - tempP1;
//						
//			rCrossingNumber += diff>0 ? diff : -diff;
//			if(DEBUG) System.out.println("R-crossing number after processing [" + i + "] = " + rCrossingNumber);
//		}
//		
//		if(DEBUG) System.out.println();
//		return rCrossingNumber;
//	}
	
	/**
	 * FOR TESTING PURPOSES ONLY
	 * 
	 * @param args
	 * @throws IOException 
	 */
	public static void main(String[] args) throws IOException 
	{
		BufferedImage inputImage = ImageIO.read(new File("./test/levels.bmp"));
		//BufferedImage inputImage = ImageIO.read(new File(".\\test\\contourEdgeImage.bmp"));
		
		Hilditch hilditch = new Hilditch(inputImage);
		BufferedImage outputImage = hilditch.thin();
		ImageIO.write(outputImage, "bmp", new File("./test/thinned.bmp"));
		
		Raster inputRaster = inputImage.getData();
		Raster thinRaster = outputImage.getData();
		
		int iEdgeCounter = 0;
		int tEdgeCounter = 0;
		for(int i = 0; i<inputImage.getHeight(); i++)
		{
			for(int j = 0; j<inputImage.getWidth(); j++)
			{
				if(inputRaster.getSample(j, i, 0)>0)
					iEdgeCounter++;
				if(thinRaster.getSample(j, i, 0)>0)
					tEdgeCounter++;				
			}
		}
		System.out.println("Quantity of edge pixels in the original image:"+iEdgeCounter);
		System.out.println("Quantity of edge pixels in the thinned image:"+tEdgeCounter);
		

	}

}