#define ARM_RATIO 0.3
#define ARM_KP 11
#define ARM_TIMEOUT (abs(additional)/30)*(100/speed)
#define STANDARD_TOLERANCE 1
#define W_RATIO 5
#define W_KP 12
#define Y_RATIO 48.5
#define Y_KP 2
#define Y_W_KP 4.5

mutex tachoMutex;

void Delay(float seconds){
  Wait(seconds*1000);
}

void Beep(long pitch, float seconds){
  PlayTone(pitch,seconds*1000);
  Delay(seconds);
}

float limitTo(float in, float limit){
  if(in<-limit) return -limit;
  else if(in>limit) return limit;
  else return in;
}

inline void RunMotor(byte port, float power, bool brake=true){
  if(power>100)
    power=100;
  if(power<-100)
    power=-100;

  if(power>0){
    OnFwdEx(port, power, RESET_NONE);
  }else if(power<0){
    OnRevEx(port, -power, RESET_NONE);
  }else if(brake){
    OffEx(port, RESET_NONE);
  }else{
    CoastEx(OUT_BC,RESET_NONE);
  }
}

inline void Drive(float y, float w=0, float throttle=1, bool brake=true){
  RunMotor(OUT_B,(y+w)*throttle,brake);
  RunMotor(OUT_C,(y-w)*throttle,brake);
}

inline void ResetWheelTachometers(){
  ResetTachoCount(OUT_B);
  ResetTachoCount(OUT_C);
}

void StraightInches(float inches, float power=100, float rampTime=0.25, bool brake=true){
  Acquire(tachoMutex);
  long bOffset=MotorTachoCount(OUT_B), cOffset=MotorTachoCount(OUT_C);
  for(unsigned int i=0; i<=(rampTime*200) && abs(inches*Y_RATIO-((MotorTachoCount(OUT_B)-bOffset+MotorTachoCount(OUT_C)-cOffset)/2)) >1; i++){
    Drive(limitTo( (inches*Y_RATIO-((MotorTachoCount(OUT_B)-bOffset+MotorTachoCount(OUT_C)-cOffset)/2)) *Y_KP,power),((MotorTachoCount(OUT_C)-cOffset)-(MotorTachoCount(OUT_B)-bOffset))*Y_W_KP,i/(rampTime*200),brake);
    Release(tachoMutex);
    Wait(5);
    Acquire(tachoMutex);
  }
  while(abs(inches*Y_RATIO-((MotorTachoCount(OUT_B)-bOffset+MotorTachoCount(OUT_C)-cOffset)/2)) >2){
    Drive(limitTo( (inches*Y_RATIO-((MotorTachoCount(OUT_B)-bOffset+MotorTachoCount(OUT_C)-cOffset)/2)) *Y_KP,power),((MotorTachoCount(OUT_C)-cOffset)-(MotorTachoCount(OUT_B)-bOffset))*Y_W_KP,1,brake);
    Release(tachoMutex);
    Wait(5);
    Acquire(tachoMutex);
  }
  for(unsigned int i=0; i<=50; i++){
    Drive(limitTo( (inches*Y_RATIO-((MotorTachoCount(OUT_B)-bOffset+MotorTachoCount(OUT_C)-cOffset)/2)) *Y_KP,power),((MotorTachoCount(OUT_C)-cOffset)-(MotorTachoCount(OUT_B)-bOffset))*W_KP/2,1,brake);
    Release(tachoMutex);
    Wait(5);
    Acquire(tachoMutex);
  }
  Release(tachoMutex);
  Drive(0,0,1,brake);
}

void StraightSeconds(float seconds, float power=100, float rampTime=0.25, bool brake=true){
  float initialTime=CurrentTick();
  Acquire(tachoMutex);
  long bOffset=MotorTachoCount(OUT_B), cOffset=MotorTachoCount(OUT_C);
  Release(tachoMutex);
  for(unsigned int i=0; i<=(rampTime*200) && CurrentTick()<(seconds*1000+initialTime); i++){
    Acquire(tachoMutex);
    Drive(power,((MotorTachoCount(OUT_C)-cOffset)-(MotorTachoCount(OUT_B)-bOffset))*Y_W_KP,i/(rampTime*200),brake);
    Release(tachoMutex);
    Wait(5);
  }
  while(CurrentTick()<(seconds*1000+initialTime)){
    Acquire(tachoMutex);
    Drive(power,((MotorTachoCount(OUT_C)-cOffset)-(MotorTachoCount(OUT_B)-bOffset))*Y_W_KP,1,brake);
    Release(tachoMutex);
    Wait(5);
  }
  for(unsigned int i=0; i<=50; i++){
    Drive(0,((MotorTachoCount(OUT_C)-cOffset)-(MotorTachoCount(OUT_B)-bOffset))*W_KP,1,brake);
    Release(tachoMutex);
    Wait(5);
    Acquire(tachoMutex);
  }
  Drive(0,0,1,brake);
}

void TurnDegrees(float degrees, float power=70, float precision=100, bool brake=true){
  Acquire(tachoMutex);
  long bOffset=MotorTachoCount(OUT_B), cOffset=MotorTachoCount(OUT_C);
  while(abs(degrees*W_RATIO- ((MotorTachoCount(OUT_B)-bOffset)-(MotorTachoCount(OUT_C)-cOffset)) ) >1){
    Drive((-((MotorTachoCount(OUT_B)-bOffset+MotorTachoCount(OUT_C)-cOffset)/2)) *Y_KP
        ,limitTo((degrees*W_RATIO- ((MotorTachoCount(OUT_B)-bOffset)-(MotorTachoCount(OUT_C)-cOffset)) ) *W_KP,power),1,brake);
    Release(tachoMutex);
    Wait(5);
    Acquire(tachoMutex);
  }
  for(unsigned int i=0;i<=precision;i++){
    Drive((-((MotorTachoCount(OUT_B)-bOffset+MotorTachoCount(OUT_C)-cOffset)/2)) *Y_KP
        ,limitTo((degrees*W_RATIO- ((MotorTachoCount(OUT_B)-bOffset)-(MotorTachoCount(OUT_C)-cOffset)) ) *W_KP/1.5,power),1,brake);
    Release(tachoMutex);
    Wait(5);
    Acquire(tachoMutex);
  }
  Release(tachoMutex);
  Drive(0,0,1,brake);
}

float armSetpoint=0;
float maxArmSpeed=100;
task armRegulator(){
  ResetTachoCount(OUT_A);
  while(true){
    Acquire(tachoMutex);
    RunMotor(OUT_A,limitTo((-armSetpoint-(MotorRotationCount(OUT_A)*ARM_RATIO))*ARM_KP,maxArmSpeed));
    Release(tachoMutex);
    Wait(5);
  }
}

void WaitForArm(float tolerance=STANDARD_TOLERANCE){
  Acquire(tachoMutex);
  while(abs(-armSetpoint-(MotorRotationCount(OUT_A)*ARM_RATIO))>=tolerance){
    Release(tachoMutex);
    Wait(6);
    Acquire(tachoMutex);
  };
  Release(tachoMutex);
}

void WaitForArmOrTime(float seconds=2, float tolerance=STANDARD_TOLERANCE){
  float initialTime=CurrentTick();
  Acquire(tachoMutex);
  while(abs(-armSetpoint-(MotorRotationCount(OUT_A)*ARM_RATIO))>=tolerance && (CurrentTick()-initialTime)<=(seconds*1000)){
    Release(tachoMutex);
    Wait(6);
    Acquire(tachoMutex);
  };
  Release(tachoMutex);
}

void SetArm(float point, float speed=100){
  maxArmSpeed=speed;
  armSetpoint=point;
}

void MoveArm(float point, float speed=100, float tolerance=STANDARD_TOLERANCE){
  maxArmSpeed=speed;
  armSetpoint=point;
  WaitForArm(tolerance);
}

void SetArmBy(float additional, float speed=100){
  maxArmSpeed=speed;
  armSetpoint+=additional;
}

void MoveArmBy(float additional, float speed=100, float tolerance=STANDARD_TOLERANCE){
  maxArmSpeed=speed;
  armSetpoint+=additional;
  WaitForArmOrTime(ARM_TIMEOUT, tolerance);
}
