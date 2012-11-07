
#include "CPExceptions.h"
#include "CPState.h"

static long iT = get_param_index("T");
static long iP = get_param_index("P");
static long iQ = get_param_index("Q");
static long iH = get_param_index("H");
static long iS = get_param_index("S");
static long iD = get_param_index("D");

void _swap (double *x, double *y)
{
	double tmp; tmp = *y; *y = *x; *x = tmp;
}
void _swap (std::string *x, std::string *y)
{
	std::string tmp; tmp = *y; *y = *x; *x = tmp;
}
void _swap (char *x, char *y)
{
	char tmp; tmp = *y; *y = *x; *x = tmp;
}
void _swap (long *x, long *y)
{
	long tmp; tmp = *y; *y = *x; *x = tmp;
}

// Constructor
CoolPropStateClass::CoolPropStateClass(std::string Fluid){
	// Set the fluid name string
	_Fluid = Fluid;
	// Try to get the index of the fluid
	long iFluid = get_Fluid_index(_Fluid);
	// If iFluid is greater than 0, it is a CoolProp Fluid, otherwise not
	if (iFluid > 0)
	{
		// Get a pointer to the fluid object
		pFluid = get_fluid(iFluid);
	}
	else
	{
		throw ValueError("Bad Fluid name - not a CoolProp fluid");
	}
}	

bool match_pair(long iI1, long iI2, long I1, long I2)
{
	return ((iI1 == I1 || iI1 == I2) && (iI2 == I1 || iI2 == I2) && iI1!=iI2);
}
void sort_pair(long *iInput1, double *Value1, long *iInput2, double *Value2, long I1, long I2)
{
	if (!(*iInput1 == I1) || !(*iInput2 == I2)){
		_swap(iInput1,iInput2);
		_swap(Value1,Value2);
	}
}
void CoolPropStateClass::check_saturated_quality(double Q){
	double mach_eps = 1e-14;

	if (fabs(Q-1) < mach_eps){
		SaturatedL = true; SaturatedV = false;
	}
	else if (fabs(Q) < mach_eps){
		SaturatedL = false; SaturatedV = true;
	}
	else{
		SaturatedL = false; SaturatedV = false;
	}
}
// Main updater function
void CoolPropStateClass::update(long iInput1, double Value1, long iInput2, double Value2){
	/* Options for inputs (in either order) are:
	|  T,P
	|  T,D
	|  H,P
	|  S,P
	|  P,Q
	|  T,Q
	|
	*/
	// If flag_SinglePhase is true, it will always assume that it is not in the two-phase region
	// Can be over-written by changing the flag to true
	flag_SinglePhase = false;

	// Don't know if it is single phase or not, so assume it isn't
	SinglePhase = false;
	
	// If the inputs are P,Q or T,Q , it is guaranteed to require a call to the saturation routine
	if (match_pair(iInput1,iInput2,iP,iQ) || match_pair(iInput1,iInput2,iT,iQ)){
		update_twophase(iInput1,Value1,iInput2,Value2);
	}
	else if (match_pair(iInput1,iInput2,iT,iD)){
		update_Trho(iInput1,Value1,iInput2,Value2);
	}
	else if (match_pair(iInput1,iInput2,iT,iP)){
		update_Tp(iInput1,Value1,iInput2,Value2);
	}
	else if (match_pair(iInput1,iInput2,iP,iH)){
		update_ph(iInput1,Value1,iInput2,Value2);
	}
	else
	{
		throw ValueError(format("Sorry your inputs didn't work"));
	}
	/*		 match_pair(iInput1,iInput2,iS,iP)){
		 // Now you need to first figure out what the phase is, and then based on that work out the rest of the parameters
		
	}*/
}
void CoolPropStateClass::update_twophase(long iInput1, double Value1, long iInput2, double Value2)
{
	// This function handles setting internal variables when the state is known to be saturated
	// Either T,Q or P,Q are given
	double Q;
	
	SinglePhase = false;
	TwoPhase = true;

	if (iInput1 == iQ){
		Q = Value1;
		sort_pair(&iInput1,&Value1,&iInput2,&Value2,iInput2,iQ);
	}
	else{
		Q = Value2;
		sort_pair(&iInput1,&Value1,&iInput2,&Value2,iInput1,iQ);
	}

	// Check whether saturated liquid or vapor
	check_saturated_quality(Q);

	if (match_pair(iInput1,iInput2,iP,iQ)){
		// Sort so they are in the order P, Q
		sort_pair(&iInput1,&Value1,&iInput2,&Value2,iP,iQ);
		// Carry out the saturation call to get the temperature and density for each phases
		if (pFluid->pure()){
			pFluid->TsatP_Pure(Value1, &TsatL, &rhosatL, &rhosatV);
			TsatV = TsatL;
		}
		else{
			TsatL = pFluid->Tsat_anc(Value1,0);
			TsatV = pFluid->Tsat_anc(Value1,1);
			psatL = Value1;
			psatV = Value1;
			// Saturation densities
			rhosatL = pFluid->density_Tp(TsatL, psatL, pFluid->rhosatL(TsatL));
			rhosatV = pFluid->density_Tp(TsatV, psatV, pFluid->rhosatV(TsatV));
		}
	}
	else{
		// Sort so they are in the order T, Q
		sort_pair(&iInput1,&Value1,&iInput2,&Value2,iT,iQ);
		// Carry out the saturation call to get the temperature and density for each phases
		if (pFluid->pure()){
			pFluid->saturation(Value1,false,&psatL,&psatV,&rhosatL,&rhosatV);
			TsatL = Value1;
			TsatV = Value1;
		}
		else{
			TsatL = Value1;
			TsatV = Value1;
			// Saturation pressures
			psatL = pFluid->psatL_anc(TsatL);
			psatV = pFluid->psatV_anc(TsatV);
			// Saturation densities
			rhosatL = pFluid->density_Tp(TsatL, psatL, pFluid->rhosatL(TsatL));
			rhosatV = pFluid->density_Tp(TsatV, psatV, pFluid->rhosatV(TsatV));
		}
	}
	// Set internal variables
	_T = Q*TsatV+(1-Q)*TsatL;
	_rho = 1/(Q/rhosatV+(1-Q)/rhosatL);
	_p = Q*psatV+(1-Q)*psatL;
	_Q = Q;
}

// Updater if T,rho are inputs
void CoolPropStateClass::update_Trho(long iInput1, double Value1, long iInput2, double Value2)
{
	// Get them in the right order
	sort_pair(&iInput1,&Value1,&iInput2,&Value2,iT,iD);

	// Set internal variables
	_T = Value1;
	_rho = Value2;

	// If either SinglePhase or flag_SinglePhase is set to true, it will not make the call to the saturation routine
	// SinglePhase is set by the class routines, and flag_SinglePhase is a flag that can be set externally
	if (!SinglePhase || !flag_SinglePhase || !pFluid->phase_Trho(_T,_rho,&psatL,&psatV,&rhosatL,&rhosatV).compare("Two-Phase"))
	{
		// If it made it to the saturation routine and it is two-phase the saturation variables have been set
		TwoPhase = true;
		SinglePhase = false;

		// Get the quality and pressure
		_Q = (1/_rho-1/rhosatL)/(1/rhosatV-1/rhosatL);
		_p = _Q*psatV+(1-_Q)*psatL;
		
		check_saturated_quality(_Q);
	}
	else{
		TwoPhase = false;
		SinglePhase = true;
		SaturatedL = false;
		SaturatedV = false;
		_p = pFluid->pressure_Trho(_T,_rho);
	}
}

// Updater if T,p are inputs
void CoolPropStateClass::update_Tp(long iInput1, double Value1, long iInput2, double Value2)
{
	// Get them in the right order
	sort_pair(&iInput1,&Value1,&iInput2,&Value2,iT,iP);

	// Set internal variables
	_T = Value1;
	_p = Value2;

	// If either SinglePhase or flag_SinglePhase is set to true, it will not make the call to the saturation routine
	// SinglePhase is set by the class routines, and flag_SinglePhase is a flag that can be set externally
	if (!SinglePhase && !flag_SinglePhase && !pFluid->phase_Tp(_T,_p,&psatL,&psatV,&rhosatL,&rhosatV).compare("Two-Phase"))
	{
		// If it made it to the saturation routine and it is two-phase the saturation variables have been set
		TwoPhase = true;
		SinglePhase = false;

		// Get the quality and pressure
		_Q = (1/_rho-1/rhosatL)/(1/rhosatV-1/rhosatL);
		_p = _Q*psatV+(1-_Q)*psatL;
		
		check_saturated_quality(_Q);
		if (pFluid->pure()){
			TsatL = _T;
			TsatV = _T;
		}
		else{
			TsatL = _T;
			TsatV = _T;
		}
	}
	else{
		TwoPhase = false;
		SinglePhase = true;
		SaturatedL = false;
		SaturatedV = false;
		_rho = pFluid->density_Tp(_T,_p);
	}
}

// Updater if p,h are inputs
void CoolPropStateClass::update_ph(long iInput1, double Value1, long iInput2, double Value2)
{
	// Get them in the right order
	sort_pair(&iInput1,&Value1,&iInput2,&Value2,iP,iH);

	// Solve for temperature and pressure
	pFluid->Temperature_ph(Value1, Value2,&_T,&_rho,&rhosatL,&rhosatV,&TsatL,&TsatV);

	// Set internal variables
	_p = Value1;

	// Set the phase flags
	if ( _T < pFluid->reduce.T && _rho < rhosatL && _rho > rhosatV)
	{
		TwoPhase = true;
		SinglePhase = false;
		_Q = (1/_rho-1/rhosatL)/(1/rhosatV-1/rhosatL);
		check_saturated_quality(_Q);

		psatL = _p;
		psatV = _p;
	}
	else
	{
		TwoPhase = false;
		SinglePhase = true;
		SaturatedL = false;
		SaturatedV = true;
	}
}

double CoolPropStateClass::h(void){
	if (TwoPhase){
		return _Q*hV()+(1-_Q)*hL();
	}
	else{
		return pFluid->enthalpy_Trho(_T,_rho);
	}
}
double CoolPropStateClass::s(void){
	if (TwoPhase){
		return _Q*sV()+(1-_Q)*sL();
	}
	else{
		return pFluid->entropy_Trho(_T,_rho);
	}
}
double CoolPropStateClass::cp(void){
	return pFluid->specific_heat_p_Trho(_T,_rho);
}
double CoolPropStateClass::cv(void){
	return pFluid->specific_heat_v_Trho(_T,_rho);
}
double CoolPropStateClass::speed_sound(void){
	return pFluid->speed_sound_Trho(_T,_rho);
}
double CoolPropStateClass::drhodT_constp(void){
	return DerivTerms("drhodT|p",_T,_rho,pFluid,SinglePhase,TwoPhase);
}
double CoolPropStateClass::drhodh_constp(void){
	return DerivTerms("drhodh|p",_T,_rho,pFluid,SinglePhase,TwoPhase);
}
double CoolPropStateClass::drhodp_consth(void){
	return DerivTerms("drhodp|h",_T,_rho,pFluid,SinglePhase,TwoPhase);
}
