/** @mainpage Arduino code
 *  @file arduino_projekt_v1
 *  Grundlagen der Informatik II, SS 2018
 *  Projekt Cocktailmischmaschiene
 *  Aufgabe 2
 *  @author Marco Baier, Nicolas Buhr, Marcel Dinse
 *  Matrikelnummern: 4444363, 4444295, 4440877
 *  @date 24.06.18 - Abgabedatum
 *  @brief Verschiedene Getränke werden mit Hilfe von Pumpen aus ihren Behältern in ein Glas befördert.
 *                Hierzu können am Computer entweder bestehende Rezepte ausgewählt oder die Mengenangaben manuell eingegeben werden.
 *                Die geforderten Mengen werden an den Arduino übertragen und dieser steuert die Pumpen.
 */

/**  
 *   Ein Globales intenger Array.
 *    Das Array sagt aus welche Pins angesteuert werden können, in diesen Fall könnte bis zu 10 Pumpen Ansteuert werden.   
 */
int pin[10] = {4,5,6,7,8,9,10,11,12,13}; 

/**
 * Ein Globales intenger Array.
 * Dieses Array wird später befüllt, wenn Python uns Daten ausgibt. Hierbei muss das Array auch aus 10 Felder bestehen,  wie das davor, da genau so viele Pumpen, wie Rezepte benötigt werden.
 */
int recepi[10] = {0,0,0,0,0,0,0,0,0,0}; 

/**
 * Ein Globales boolean Variable.
 * Diese ist auf false da sonst sie Pumpen dauerhaft arbeiten würden
 */
boolean started = false; 

/**
 * Ein Globales boolean Variable.
 * Diese muss auf false sein, da man sonst nur einmal ein rezept von Python bekommt und dieses dann immer wieder ausgeführt werden wird.
 */
boolean input = false; 

/**
 * Ein Globales float Variable.
 * Rechen Wert für die Pumpen. Da die Pumpen nach einer bestimmten Zeit schnell pumpen, muss ein Wert bestimmt werden, um das Glas richtig zu füllen.
 */
float millisecond_per_cl = 160; 

/**
 * Ein Globales long Variable
 * Diese ist dafür da um die Zeit zu speichern.
 */
long zeit;

/**
 * Ein Globales intenger Variable
 * Für die Anzahl der Pumpen die aktiv sind.
 */
int number_running;

/**
 * Ein include.
 * Seriale Kommunikation über andere pins als die standard pins.
 */
#include <SoftwareSerial.h> 
/**
 * Ein include.
 * Dies wird hinzugefügt um eine Kommunikation über Wlan zu erstellen.
 */
#include "DumbServer.h" 

/**
 * Ein SoftwareSerial
 * esp_serial mit zwei Argumenten. Die zwei Argumente sind für die Pins und für die Kommunikation des Wlan Moduls da.
 */
SoftwareSerial esp_serial(3, 2); 

/**
 * Ein Objekt.
 * Es wird ein Objekt EspServer als esp_server aus dem DumbServer gespeichert.
 */
EspServer esp_server; 

/** 
 *  @brief Ein Funktion test_for_new.
 *  
 * Diese Funktion ist dafür da um zu überprüfen ob ein neues Rezept geschickt wurde.
 */
void test_for_new()
{
  /** 
   *  @brief Eine if Bedingung.  
   *  @param esp_server.available ist dafür da um zu testen ob es ein signal bekommen hat, wenn ja geht er in die if schleife rein.
   */
  if(esp_server.available())
  {
    String input_string = esp_server.readStringUntil('\n'); /**< Ein Lokales String Variable. Dieses ist dafür da um die eingespeicherten Zahlen zu trennen.*/
    int j = 0;  /**< Ein Lokales intenger Variable, dieses wird auf 0 gesetzt. */
    int n = 0;  /**< Ein Lokales intenger Variable, dieses wird auf 0 gesetzt. */
    
    /** 
     *  @brief Eine for Schleife 
     *  
     * @param i = 0 als ein integer
     * @param i< input_string.length() bedingung für die Schleife
     * @param i++ nach ausführung der Schleife wird i +1 gesetzt
     */
    for(int i=0; i<input_string.length(); i++) 
    {
      /** 
       *  @brief Eine if Bedingung
       *  
       *  @param input_strin[i]==',' 
       *  die if bedingung ist erfüllt wenn im input string etwas drin steht.
       */
      if(input_string[i]==',')
      {
        recepi[j]=n; /**< Das Globale recepi array wird auf n  */
        n = 0; /**< Die Lokale Variable wird nochmal auf 0 gesetzt. */
        j++;  /**< Die Lokale Variable wird immer um 1 erhöt. */
      }
      /** @brief Eine else Bedingung
      /*
       * Diese wird ausgeführt wenn die die obrige if Bedingung nicht erfüllt wird
       */
      else
      {
         n = (n*10)+int(input_string[i])-48; /**< else integer n wird verzehnfacht, mit int()-48 wird das aktuelle Zeichen aus der UTF-8 codierung in eine Dezimalzahl übersetzt. */
      }
    }
    input = true; /**< if boolean input wird auf true gesetzt damit das Hauptprogramm starten kann */
  }
}
/** @brief Die Funktion setup()
 *
 * Diese Funktion ist dafür da um alle dinge einmal durch zuführen um zu Starten.
 */

void setup()
{
  /**
   *  Ein Serial.begin.
   * Damit die kommunikation mit serialen monitor beginnt.
   */
  Serial.begin(9600); 
  /**
   * Ein esp_serial.begin.
   *  Das gleiche für das Wlan Modul.
   */
  esp_serial.begin(9600);  
  /**
   * Ein Serial.println.
   * Er schreibt in den Serial Monitor "Starting server ..."
   */
  Serial.println("Starting server..."); 
  /**
   * Ein esp_server.Begin.
   * Er sagt dem Wlan Modul,das er sich mit dem Wlan Netz und Modul verbinden soll und das der port 30303 von arduino ist.
   */
  esp_server.begin(&esp_serial, "arduino", "password", 30303); 
  /**
   * Ein Serial.println.
   * er schreibt wieder in den Serial Monitor "... server is running".
   */
  Serial.println("...server is running");  
  /**
   * Ein char Liste.
   * ip[16] mit 16 zeichen.
   */
  char ip[16];
  /**
   * Ein esp_server.my_ip.
   * Es wird vom Wlan Modul die IP-Adresse ab gefragt und speichert diese ein. 
   */
  esp_server.my_ip(ip, 16);
  /**
   * Ein Serial.print
   * Im Serial Monitor wird "My ip:" geschrieben. 
   */
  Serial.print("My ip: ");
  /**  
   * Ein Serial.println
   * Im Serial Monitor wird die IP-Adresse ausgegeben welche vorher eingespeichert wurde.
   */
  Serial.println(ip);  

  /** @brief for Schleife. 
   *  Um die Pins zu deklaieren.
   * @param integer i = 0 
   * @param i < 10 als Bedingung für die schleife
   * @param i++ i wird immer um 1 erhöht
   */
  for(int i=0; i<10; i++)
  {
    pinMode(pin[i], OUTPUT); /**< pinMode(pin[i], OUTPUT) ist dafür da um die Pins als Ausgang zu definieren. */
    digitalWrite(pin[i], HIGH); /**< digitalWrite(pin[i], HIGH) die jeweiligen Pins werden kurz auf 1 gesetzt, weil die Hardware mit den Relais normally closed sind, sprich sie sind öffner.*/
  }
}
/** 
 *  @brief Die Funktion loop.
 *  
 * Hier wird alles ausgeführt und dort steht das Hauptprogramm.
 */

void loop(){
  /** 
   *  @brief if Bedingung. 
   *  
   *  @param input == false es wird verglichen ob input auf false ist.
   */
  if(input == false)
  {
    test_for_new(); /**< test_for new() soll so lange überprüft werden, bis es Rezepte bekommt und in der Funktion input auf true setzt. */
  }
  /** 
   *  @brief if Bedingung.
   *  
   *  @param input == true es wird überprüft ob input auf true gesetzt ist.
   */
  if(input == true)
  {
    /** 
     *  @brief if Bedingung. 
     *  
     *  @param started == false es wird wie vorher bei input jetzt started überprüft ob es auf false gesetzt ist.
     */
    if(started == false)
    {
      number_running = 0; /**< numer_running = 0 hier wird die Variable auf 0 gesetzt. */
      
      /** 
       *  @brief for Schleife. 
       * Diese schleife ist dafür da um die Pumpen zu aktivieren.
       * @param integer i=0 
       * @param i<10 Bedingung für die Schleife
       * @param i++ i wird immer um eins erhöht
       */
      for(int i=0; i<10; i++)
      {
        /** 
         *  @brief if Bedingung.
         *  
         * @param array recepi[i]!=0 darf nicht gleich null sein, desweiteren ist die if Bedingung dafür da um die Pumpen zu aktivieren.
         */
        if(recepi[i]!=0)
        {
          digitalWrite(pin[i], LOW); /**< digitalWrite(pin[i],LOW jetzt werden die Pumpem Aktiviert. Es wird aber auf LOW gesetzt, weil die Relais öffner sind.  */
          number_running++; /**< number_running++ wird immer um 1 erhöht, dadurch weiß man wieviele Pumpen in dem Moment aktiv sind */
        }
      }
      zeit = millis(); /**< zeit = millis() die Variable zeit wird gleich die Funktion millis() gesetzt.  */
      started = true; /**< started = true nachdem alle Pumpem aktiv sind wird started auf true gesetzt */
    }
    /** 
     *  @brief if Bedingung.
     *  
     * @param started == true es wird verglichen ob started auf true gesetzt wurde
     */
    if(started == true)
    {
      /** 
       *  @brief for Schleife 
       * Diese Schleife ist dafür da um die Pumpen/relais zu deaktivieren.
       * @param integer i=0 
       * @param i<10 die Bedingung für die Schleife
       * @param i++ i wird immer um 1 erhöht
       */
      for(int i=0; i<10; i++)
      {
        /** 
         *  @brief if Bedingung
         *  
         *  @param !digitalRead(pin[i]) es wird getest ob die jeweiligen pins auf LOW stehen.
         */
        if(!digitalRead(pin[i]))
        {
          /** 
           *  @brief if Bedingung
           *  
           * @param zeit+(recepi[i]*millisecond_per_cl)+200<millis() es wird geprüft ob die zeit die, die Pumpem aktiv sind kleiner ist als bei millis() 
           */
          if(zeit+(recepi[i]*millisecond_per_cl)+200<millis())
          {
            digitalWrite(pin[i], HIGH); /**< digitalWrite(pin[i], HIGH) wenn die jeweilige Zeit des Arrays vorbei ist schaltet der Befehl die dazu gehörige Pumpe aus also stellt sie auf 1, da wir einen Öffner nutzen */
            number_running--; /**< number_running-- ddadurch wird einfach die Variable jedes mal um 1 gesenkt. */
          }
        }
      }
      /** 
       *  @brief if Bedingung 
       * Die if Bedingung ist dafür da um die Variablen die für den start sorgen wieder zu ändern wenn number_running auf den Wert 0 ist.
       * @param number_running == 0
       */
      if(number_running == 0)
      {
        started = false; /**< started wird auf false gesetzt damit der Pump Vorgang nur einmal ausgeführt wird. */
        input = false; /**< input wird auf false gesetzt damit die rezepte wieder auf 0 gesetz werden und man auf neue rezepte wartet bis es starten kann */
      }
    }
  }
}

