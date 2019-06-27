#define XPLM200

#include <stdio.h>
#include "XPLMUtilities.h"
#include "XPLMDataAccess.h"
#include "XPLMProcessing.h"
#include "XPLMPlugin.h"

#if IBM
#include <windows.h>
#endif
#if LIN
#include <GL/gl.h>
#elif __GNUC__
#include <OpenGL/gl.h>
#else
#include <GL/gl.h>
#endif

/*FLCB (Flight loop callbacks)*/
float RunOnceAtStartup(float, float, int, void *);
float RunEveryFrame(float, float, int, void *);


/*
* Gets the Opaque (How the data/command is actually represented for reading and writing in X-Plane) 
* of the data/command ref we want to utilize
*/
XPLMDataRef DataName = XPLMFindDataRef("sim/flightmodel/position/y_agl");
XPLMCommandRef CommandRef = XPLMFindCommand("sim/view/chase");



/*
 * XPluginStart
 */
PLUGIN_API int XPluginStart(char * outName, char * outSig, char * outDesc)
{
	strcpy(outName, "AutoLoadSit");
	strcpy(outSig, "xplanesdk.plugin.AutoLoadSit");
	strcpy(outDesc, "A plugin that automatically loads a situation file when plane falls under a certain altitude.");

	/* Calls the loop callback*/
	XPLMRegisterFlightLoopCallback(RunOnceAtStartup, -1.0, NULL);
	XPLMRegisterFlightLoopCallback(RunEveryFrame, -1.0, NULL);

	/* We must return 1 to indicate successful initialization, otherwise we
	 * will not be called back again. */
	return 1;
}




/*
 * XPluginStop
 * Our cleanup routine unregisters the callbacks
 */
PLUGIN_API void	XPluginStop(void)
{
	XPLMUnregisterFlightLoopCallback(RunOnceAtStartup, NULL);
	XPLMUnregisterFlightLoopCallback(RunEveryFrame, NULL);
}




/*
 * XPluginDisable
 * We do not need to do anything when we are disabled, but we must provide the handler.
 */
PLUGIN_API void XPluginDisable(void)
{
}




/*
 * XPluginEnable.
 * We don't do any enable-specific initialization, but we must return 1 to indicate
 * that we may be enabled at this time.
 */
PLUGIN_API int XPluginEnable(void)
{
	return 1;
}




/*
 * XPluginReceiveMessage
 * We don't have to do anything in our receive message handler, but we must provide one.
 */
PLUGIN_API void XPluginReceiveMessage(XPLMPluginID inFromWho, int inMessage, void * inParam)
{
}




/*FLCB callbacks*/

/*
* If the plane falls under the altitude value, minAltitude, then reload the plane
* in the air by reloading the situation file with the given PATH.
* Afterwards, XPLMCommandOnce executes the command to change the view to third-person
* Note that the data ref for the altitude is in meters
*/

/*Function taken at startup of simulation*/
float RunOnceAtStartup(float, float, int, void *) {

	float minAltitude = XPLMGetDataf(DataName);

	if (minAltitude <= 500)
	{
		XPLMLoadDataFile(xplm_DataFile_Situation, "Output/situations/good.sit");
		XPLMCommandOnce(CommandRef);
	}


	return 0;   //return 0 to not run again
}



/*Function taken at every frame of simulation*/
float RunEveryFrame(float, float, int, void *) {

	float minAltitude = XPLMGetDataf(DataName);

	if (minAltitude <= 100)
	{
		XPLMLoadDataFile(xplm_DataFile_Situation, "Output/situations/good.sit");
		XPLMCommandOnce(CommandRef);
	}


	return -1.0; //return -1 to run again next frame
}