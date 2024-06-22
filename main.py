from picamera2 import Picamera2, Preview
from ultralytics import YOLO
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import time


def identify_pet():
    output = []
    model = YOLO("yolov8l.pt")
    results = model.predict("test.jpg")
    result = results[0]

    for box in result.boxes:
        class_id = result.names[box.cls[0].item()]

        if (class_id == "cat"):
            output.append(class_id)
        elif (class_id == "dog"):
            output.append(class_id)
    return output

def take_photo(picam2):
    
    camera_config = picam2.create_preview_configuration({"size":(1920,1080)})
    picam2.configure(camera_config)
    picam2.start_preview(Preview.QTGL)
    picam2.start()
    time.sleep(5)
    picam2.capture_file("test.jpg")
    picam2.stop_preview()
    picam2.stop()
    time.sleep(1)

def rfid_detect(reader):
    while True:
        time.sleep(1)
        if reader.read_id() != None:
            print("RFID Detected")
            return True
        else:
            continue

def motor1_run(in1,in2):
    """
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.HIGH)
    GPIO.output(in1,GPIO.HIGH)
    GPIO.output(in2,GPIO.LOW)
    """
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.HIGH)
    time.sleep(0.25)
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.HIGH)
    time.sleep(0.25)
    """
    time.sleep(0.25)
    GPIO.output(in1,GPIO.HIGH)
    GPIO.output(in2,GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.LOW)
    """
    
    print("turning off motor 1")
    GPIO.output(in1, False)
    GPIO.output(in2,False)
    GPIO.output(in1, True)
    GPIO.output(in2,True)

def motor2_run(in3,in4):
    """
    GPIO.output(in3,GPIO.LOW)
    GPIO.output(in4,GPIO.HIGH)
    GPIO.output(in3,GPIO.HIGH)
    GPIO.output(in4,GPIO.LOW)
    """
    GPIO.output(in3,GPIO.LOW)
    GPIO.output(in4,GPIO.HIGH)
    time.sleep(0.25)
    GPIO.output(in3,GPIO.LOW)
    GPIO.output(in4,GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(in3,GPIO.LOW)
    GPIO.output(in4,GPIO.HIGH)
    time.sleep(0.25)
    print("turning off motor 2")
    GPIO.output(in3,False)
    GPIO.output(in4,False)
    GPIO.output(in3,True)
    GPIO.output(in4,True)
    
    
def dispense_food(type,in1,in2,in3,in4,last_fed):
    if len(type) <1:

        print("No pet Detected")

        main1(last_fed,feeding_interval,reader,picam2,power_a,power_b)
    else:
        for i in type:
            if i == "cat":
                print("dispense cat food")
                motor2_run(in3,in4)
                
                main1(last_fed,feeding_interval,reader,picam2,power_a,power_b)
            elif i == "dog":
                print("dispense dog food")
                motor1_run(in1,in2)
                
                main1(last_fed,feeding_interval,reader,picam2,power_a,power_b)
            else:
                print("id is not a cat or dog")

def main1(last_fed,feeding_interval,reader,picam2,power_a,power_b):
    #GPIO.cleanup()
    #time.sleep(2)
    
    time_difference = 0

    isDetected = rfid_detect(reader) # returns true if an rfid is detected

    try:
        if isDetected:
            current_time = time.time()
            print(current_time)
            print(last_fed)
            print(time_difference)
            time_difference = (current_time - last_fed)
            if time_difference >= feeding_interval:
                    
                    time.sleep(0.5)
                    last_fed = time.time()
                    #print(time_difference)
                    #print(reader.read_id()

                    take_photo(picam2)
                    pet_ids = identify_pet()
                    print("pets ID'd", pet_ids)
                    #GPIO.cleanup()
                    dispense_food(pet_ids,in1,in2,in3,in4,last_fed)

                    #if pet_detected == False:
                        
                    
            else:

                print("not feeding time")
                print("Next feeding available",time_difference)
                main1(last_fed,feeding_interval,reader,picam2,power_a,power_b)

    except KeyboardInterrupt:
        power_a.stop()
        power_b.stop()
        print("keyboard interrupt cleanup")
        GPIO.cleanup()
    finally:
        power_a.stop()
        power_b.stop()
        GPIO.cleanup()
        
        


#GPIO.cleanup()


if __name__ == "__main__":

    """ This is executed when run from the command line """

    #set to last time fed/ activated
    
    in1 =11 #GPIO/BCM = 17 | BOARD = 11
    in2 = 13 #GPIO/BCM = 27 | BOARD = 13
    en_a = 32 #GPIO/BCM = 12 | BOARD = 32

    in3 = 36 #GPIO/BCM = 16 | BOARD = 36
    in4 = 37 #GPIO/BCM = 26 | BOARD = 37
    en_b = 35 #GPIO/BCM = 19 |BOARD = 35
    #setup the output pins
    #GPIO.setmode(GPIO.BCM)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False) 
    #motor 1
    GPIO.setup(in1,GPIO.OUT)
    GPIO.setup(in2,GPIO.OUT)
    GPIO.setup(en_a,GPIO.OUT)
                                
    power_a = GPIO.PWM(en_a,50) #channel 12 frequency 50 Hz
    
    power_a.start(50)

    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.LOW)

    #motor 2
    GPIO.setup(in3,GPIO.OUT)
    GPIO.setup(in4,GPIO.OUT)
    GPIO.setup(en_b,GPIO.OUT)
    power_b = GPIO.PWM(en_b,50)#channel 19 frequency 50 Hz
    power_b.start(50)

    #sanity check
    GPIO.output(in3,GPIO.LOW)
    GPIO.output(in4,GPIO.LOW)

    last_fed = 0 
    feeding_interval = 30 #change to user input
    reader = SimpleMFRC522() 
    picam2 = Picamera2()

    main1(last_fed,feeding_interval,reader,picam2,power_a,power_b)
