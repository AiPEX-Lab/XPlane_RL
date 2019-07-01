
/*
 * HellWorld.c
 * 
 * This plugin implements the canonical first program.  In this case, we will 
 * create a window that has the text hello-world in it.  As an added bonus
 * the  text will change to 'This is a plugin' while the mouse is held down
 * in the window.  
 * 
 * This plugin demonstrates creating a window and writing mouse and drawing
 * callbacks for that window.
 * 
 */

#define XPLM200

#include <stdio.h>
#include <string.h>
#include <sstream>
#include <iostream>
#include <string>
#include "XPLMDisplay.h"
#include "XPLMUtilities.h"
#include "XPLMDataAccess.h"
#include "XPLMProcessing.h"
#include "XPLMPlugin.h"
#include "XPLMGraphics.h"


using namespace std;


/*
 * Global Variables.  We will store our single window globally.  We also record
 * whether the mouse is down from our mouse handler.  The drawing handler looks
 * at this information and draws the appropriate display.
 * 
 */

template<typename T>
string ftos(T i)
{
	stringstream s;
	s << i;
	return s.str();
}

// FLCB (Flight loop callbacks)
float RunOnceAtStartup(float, float, int, void *);
float RunEveryFrame(float, float, int, void *);

static XPLMWindowID	gWindow = NULL;
static int				gClicked = 0;

static void MyDrawWindowCallback(
                                   XPLMWindowID         inWindowID,    
                                   void *               inRefcon);    

static void MyHandleKeyCallback(
                                   XPLMWindowID         inWindowID,    
                                   char                 inKey,    
                                   XPLMKeyFlags         inFlags,    
                                   char                 inVirtualKey,    
                                   void *               inRefcon,    
                                   int                  losingFocus);    

static int MyHandleMouseClickCallback(
                                   XPLMWindowID         inWindowID,    
                                   int                  x,    
                                   int                  y,    
                                   XPLMMouseStatus      inMouse,    
                                   void *               inRefcon);    


/*
* Gets the Opaque (How the data is actually represented for reading and writing in X-Plane) of the data ref we want to utilize
*/
XPLMDataRef DataName = XPLMFindDataRef("sim/flightmodel/position/y_agl");

float currAltitude = XPLMGetDataf(DataName);
//string ss = ftos(currAltitude);
//const char* currAltitudeChar = ss.c_str();

/*
 * XPluginStart
 * 
 * 
 */
PLUGIN_API int XPluginStart(char * outName,char * outSig, char * outDesc)
{
	strcpy(outName, "HelloWorld");
	strcpy(outSig, "xplanesdk.examples.helloworld");
	strcpy(outDesc, "A plugin that makes a window.");

	/* Now we create a window.  We pass in a rectangle in left, top,
	 * right, bottom screen coordinates.  We pass in three callbacks. */




		// FLCB
	XPLMRegisterFlightLoopCallback(RunOnceAtStartup, -1.0, NULL);
	XPLMRegisterFlightLoopCallback(RunEveryFrame, -1.0, NULL);

/* We must return 1 to indicate successful initialization, otherwise we
 * will not be called back again. */

	return 1;
	/*
	if (currAltitude <= 500)
	{
		XPLMLoadDataFile(xplm_DataFile_Situation, "Output\situations\inAir2.sit");
	}
	*/

}

/*
 * XPluginStop
 * 
 * Our cleanup routine deallocates our window.
 * 
 */
PLUGIN_API void	XPluginStop(void)
{

	XPLMUnregisterFlightLoopCallback(RunOnceAtStartup, NULL);
	XPLMUnregisterFlightLoopCallback(RunEveryFrame, NULL);

	XPLMDestroyWindow(gWindow);
}

/*
 * XPluginDisable
 * 
 * We do not need to do anything when we are disabled, but we must provide the handler.
 * 
 */
PLUGIN_API void XPluginDisable(void)
{
}

/*
 * XPluginEnable.
 * 
 * We don't do any enable-specific initialization, but we must return 1 to indicate
 * that we may be enabled at this time.
 * 
 */
PLUGIN_API int XPluginEnable(void)
{
	return 1;
}

/*
 * XPluginReceiveMessage
 * 
 * We don't have to do anything in our receive message handler, but we must provide one.
 * 
 */
PLUGIN_API void XPluginReceiveMessage(XPLMPluginID inFromWho, int inMessage, void * inParam)
{
}

/*
 * MyDrawingWindowCallback
 *
 * This callback does the work of drawing our window once per sim cycle each time
 * it is needed.  It dynamically changes the text depending on the saved mouse
 * status.  Note that we don't have to tell X-Plane to redraw us when our text
 * changes; we are redrawn by the sim continuously.
 *
 */
void MyDrawWindowCallback(
	XPLMWindowID         inWindowID,
	void *               inRefcon)
{
	int		left, top, right, bottom;
	float	color[] = { 1.0, 1.0, 1.0 }; 	/* RGB White */

	float currAltitude = XPLMGetDataf(DataName);
	string ss = ftos(currAltitude);
	const char* currAltitudeChar = ss.c_str();

	/* First we get the location of the window passed in to us. */
	XPLMGetWindowGeometry(inWindowID, &left, &top, &right, &bottom);

	/* We now use an XPLMGraphics routine to draw a translucent dark
	 * rectangle that is our window's shape. */
	XPLMDrawTranslucentDarkBox(left, top, right, bottom);

	/* Finally we draw the text into the window, also using XPLMGraphics
	 * routines.  The NULL indicates no word wrapping. */
	XPLMDrawString(color, left + 5, top - 20,
		//(char*)(gClicked ? "I'm a plugin" : "Hello world"), NULL, xplmFont_Basic);
		(char*)(gClicked ? currAltitudeChar : currAltitudeChar), NULL, xplmFont_Basic);


}

/*
 * MyHandleKeyCallback
 *
 * Our key handling callback does nothing in this plugin.  This is ok;
 * we simply don't use keyboard input.
 *
 */
void MyHandleKeyCallback(
	XPLMWindowID         inWindowID,
	char                 inKey,
	XPLMKeyFlags         inFlags,
	char                 inVirtualKey,
	void *               inRefcon,
	int                  losingFocus)
{
}

/*
 * MyHandleMouseClickCallback
 *
 * Our mouse click callback toggles the status of our mouse variable
 * as the mouse is clicked.  We then update our text on the next sim
 * cycle.
 *
 */
int MyHandleMouseClickCallback(
	XPLMWindowID         inWindowID,
	int                  x,
	int                  y,
	XPLMMouseStatus      inMouse,
	void *               inRefcon)
{
	/* If we get a down or up, toggle our status click.  We will
	 * never get a down without an up if we accept the down. */
	if ((inMouse == xplm_MouseDown) || (inMouse == xplm_MouseUp))
		gClicked = 1 - gClicked;

	/* Returning 1 tells X-Plane that we 'accepted' the click; otherwise
	 * it would be passed to the next window behind us.  If we accept
	 * the click we get mouse moved and mouse up callbacks, if we don't
	 * we do not get any more callbacks.  It is worth noting that we
	 * will receive mouse moved and mouse up even if the mouse is dragged
	 * out of our window's box as long as the click started in our window's
	 * box. */
	return 1;
}


// FLCB callbacks
float RunOnceAtStartup(float, float, int, void *) {

	// Code goes here!

	gWindow = XPLMCreateWindow(
		50, 600, 300, 200,			/* Area of the window. */
		1,							/* Start visible. */
		MyDrawWindowCallback,		/* Callbacks */
		MyHandleKeyCallback,
		MyHandleMouseClickCallback,
		NULL);						/* Refcon - not used. */

	float currAltitude = XPLMGetDataf(DataName);

	if (currAltitude <= 500)
	{
		XPLMLoadDataFile(xplm_DataFile_Situation, "Output\\situations\\inAir2.sit");
	}


	return 0;   //return 0 to not run again
}

float RunEveryFrame(float, float, int, void *) {

	// Code goes here!


	gWindow = XPLMCreateWindow(
		50, 600, 300, 200,			/* Area of the window. */
		1,							/* Start visible. */
		MyDrawWindowCallback,		/* Callbacks */
		MyHandleKeyCallback,
		MyHandleMouseClickCallback,
		NULL);						/* Refcon - not used. */

	float currAltitude = XPLMGetDataf(DataName);

	if (currAltitude <= 500)
	{
		XPLMLoadDataFile(xplm_DataFile_Situation, "Output\\situations\\inAir2.sit");
	}


	return -1.0; //return -1 to run again next frame
}