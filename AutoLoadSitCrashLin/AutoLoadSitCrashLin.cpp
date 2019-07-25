#include <stdio.h>
#include <string.h>
#include "XPLMUtilities.h"
#include "XPLMDataAccess.h"
#include "XPLMProcessing.h"
#include "XPLMPlugin.h"
#include <stdlib.h> 

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

#ifndef XPLM300
	#error This is made to be compiled against the XPLM300 SDK
#endif



// FLCB (Flight loop callbacks)
float RunOnceAtStartup(float, float, int, void *);
float RunEveryFrame(float, float, int, void *);


/*
* Gets the Opaque (How the data/command is actually represented for reading and writing in X-Plane) 
* of the data/command ref we want to utilize
*/
XPLMDataRef gforce_normal = XPLMFindDataRef("sim/flightmodel2/misc/gforce_normal");
XPLMDataRef gforce_axil = XPLMFindDataRef("sim/flightmodel2/misc/gforce_axil");
XPLMDataRef gforce_side = XPLMFindDataRef("sim/flightmodel2/misc/gforce_side");
XPLMDataRef crashed = XPLMFindDataRef("sim/flightmodel2/misc/has_crashed");
XPLMDataRef gspeed = XPLMFindDataRef("sim/flightmodel/position/groundspeed");
XPLMDataRef ground_contact = XPLMFindDataRef("sim/flightmodel2/gear/on_ground");
XPLMDataRef DataName = XPLMFindDataRef("sim/flightmodel/position/y_agl");
XPLMDataRef simtime = XPLMFindDataRef("sim/time/total_running_time_sec");
XPLMCommandRef CommandRef = XPLMFindCommand("sim/view/chase");



/*
 * XPluginStart
 */
PLUGIN_API int XPluginStart(char * outName,char * outSig, char * outDesc)
{
	strcpy(outName, "AutoLoadLinCrash");
	strcpy(outSig, "xplanesdk.plugin.AutoLoadLinCrash");
	strcpy(outDesc, "A plugin that automatically loads a situation file.");

	/* Calls the loop callback*/
	XPLMRegisterFlightLoopCallback(RunOnceAtStartup, -1.0, NULL);
	XPLMRegisterFlightLoopCallback(RunEveryFrame, -1.0, NULL);

/* We must return 1 to indicate successful initialization, otherwise we
 * will not be called back again. */

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




/*FLCB callbacks*/

/*
* If the plane exceeds a certain g-force, maxGForce, then reload the plane
* in the air by reloading the situation file with the given PATH.
* Afterwards, XPLMCommandOnce executes the command to change the view to third-person
* Note that the data ref for the altitude is in g's
*/

/*Function taken at startup of simulation*/
float RunOnceAtStartup(float, float, int, void *) {

	float minAltitude = XPLMGetDataf(DataName);
	float normal = XPLMGetDataf(gforce_normal);
	float axil = XPLMGetDataf(gforce_axil);
	float side = XPLMGetDataf(gforce_side);
	int crashed_yes = XPLMGetDataf(crashed);
	float speed = XPLMGetDataf(gspeed);
	float time = XPLMGetDataf(simtime);
	double counter = 0;

	if (abs(normal) >= 6 || abs(axil) >= 6 || abs(side) >= 6 || crashed_yes == 1)
	{
		XPLMLoadDataFile(xplm_DataFile_Situation, "Output\\situations\\keepHeading.sit");
		XPLMCommandOnce(CommandRef);
	}

	else if (speed <= 5 && minAltitude <=5)// || contact > 0)
	{
		XPLMLoadDataFile(xplm_DataFile_Situation, "Output\\situations\\keepHeading.sit");
		XPLMCommandOnce(CommandRef);	
	}

	else if (time >= 62.35)
	{
		XPLMLoadDataFile(xplm_DataFile_Situation, "Output\\situations\\keepHeading.sit");
		XPLMCommandOnce(CommandRef);
	}

	/* 
	if (minAltitude < 0.1){
		//sleep(10);


		for(double i = 0; i<=100000000000000000000000000000000000000000000000000; i++){
			counter += 1;
		}
		if(counter > 100000000000000000000000000000000000000000000000000){
		XPLMLoadDataFile(xplm_DataFile_Situation, "Output\\situations\\landing02.sit");
		XPLMCommandOnce(CommandRef);}
	}*/
	return 0;   
	/*return 0 to not run again*/

}

/*Function taken at every frame of simulation*/
float RunEveryFrame(float, float, int, void *) {

	float minAltitude = XPLMGetDataf(DataName);
	float normal = XPLMGetDataf(gforce_normal);
	float axil = XPLMGetDataf(gforce_axil);
	float side = XPLMGetDataf(gforce_side);
	int crashed_yes = XPLMGetDataf(crashed);
	float speed = XPLMGetDataf(gspeed);
	float time = XPLMGetDataf(simtime);
	double counter = 1;


	if (abs(normal) >= 6 || abs(axil) >= 6 || abs(side) >= 6 || crashed_yes == 1)
	{
		XPLMLoadDataFile(xplm_DataFile_Situation, "Output\\situations\\keepHeading.sit");
		XPLMCommandOnce(CommandRef);
	}

	else if (speed <= 5 && minAltitude <=5)// || contact > 0)
	{
		XPLMLoadDataFile(xplm_DataFile_Situation, "Output\\situations\\keepHeading.sit");
		XPLMCommandOnce(CommandRef);	
	}

	else if (time >= 62.35)
	{
		XPLMLoadDataFile(xplm_DataFile_Situation, "Output\\situations\\keepHeading.sit");
		XPLMCommandOnce(CommandRef);
	}

	/* 
	if (minAltitude < 0.1){
		//sleep(10);


		for(double i = 0; i<=100000000000000000000000000000000000000000000000000; i++){
			counter += 1;
		}
		if(counter > 100000000000000000000000000000000000000000000000000){
		XPLMLoadDataFile(xplm_DataFile_Situation, "Output\\situations\\landing02.sit");
		XPLMCommandOnce(CommandRef);}
	}*/



	return -1.0;
	/*return -1 to run again next frame*/
}