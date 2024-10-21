1. GUI Dialogs and Handlers

* `Dialog1` (Main Window):
    * Objects:
        * `Lookupbutton`: Triggers the `DoScrape` subroutine to fetch order data.
        * `Shipbutton`: Triggers the `DoShip` subroutine to initiate shipping.
        * `shipbut1-9`:  Buttons to copy shipping information to the clipboard (e.g., `DoName`, `DoCompany`, etc.).
        * `PartButton`: Triggers the `DoPart` subroutine for partial shipments.
        * `autobut1`: Triggers the `DoGO` subroutine for automatic shipping.
        * `editinvoice`: Triggers the `Doinvoiceedit` subroutine to open the invoice editing window.
        * `reportissue`: Triggers the `Doasanaissue` subroutine to open the Asana issue reporting window.
        * `listorders`: Triggers the `showordersinlist` subroutine to open the order list window.
        * `ManButton1`: Opens the manual shipping dialog (`Dialog6`).
    * Handlers: Each button is linked to its corresponding subroutine using `AddDialogHandler`. 
        
* `Dialog2` (Length Check):
    * Objects: 
        * `D2Button1`: Triggers the `Dolengthchange` subroutine to handle address length changes.
        * `D2Button2`: Triggers the `Docountlines` subroutine to count characters in the input fields.
    * Handlers: Linked to their subroutines with `AddDialogHandler`.

* `Dialog3` (Character Replacement):
    * Objects:
        * `D2Button1`:  Triggers the `Domessageclose` subroutine to close the dialog.
    * Handlers: Linked to the subroutine using `AddDialogHandler`.

* `Dialog4` (Query):
    * Objects:
        * `queryyes`:  Triggers the `Domessageclose` subroutine to close the dialog.
        * `queryno`: Triggers the `Domessageclose` subroutine to close the dialog.
    * Handlers: Linked to the subroutine using `AddDialogHandler`.

* `Dialog5` (Shipping List):
    * Objects:
        * `d5MSButton1`: Triggers the `shippre` subroutine to move to the previous order.
        * `d5MSButton2`: Triggers the `shipnext` subroutine to move to the next order.
        * `d5MSButton3`: Triggers the `gomanship` subroutine to manually ship the selected order.
        * `d5MSButton4`: Triggers the `goautoship` subroutine to automatically ship all orders.
        * `d5MSButton5`: Triggers the `shipdata` subroutine to load data from the shipping schedule file.
        * `d5MSButton6`: Triggers the `shipfileedit` subroutine to open the shipping schedule file in Notepad.
        * `d5MSButton7`: Triggers the `shiplookup` subroutine to search for a specific order number in the shipping schedule.
        * `d5MSButton8`: Triggers the `shippre5` subroutine to jump 5 orders back.
        * `d5MSButton9`: Triggers the `shipnext5` subroutine to jump 5 orders forward.
    * Handlers: Linked to their corresponding subroutines using `AddDialogHandler`.

* `Dialog6` (Manual Shipping):
    * Objects:
        * `d6button`: Triggers the `DoMANGO` subroutine for manual shipping.
        * `d6button2`: Triggers the `manualshipgrab` subroutine to grab shipping details from the main window.
        * `d6button3`: Triggers the `DoPartMANGO` subroutine for partial manual shipping.
    * Handlers: Linked to their corresponding subroutines using `AddDialogHandler`.

* `Dialog7` (Can't Ship):
    * Objects: None
    * Handlers: None

* `Dialog8` (RM Package Size):
    * Objects:
        * `MSButton1`: Triggers the `setletter` subroutine to select "Letter" package type.
        * `MSButton2`: Triggers the `setlletter` subroutine to select "Large Letter" package type.
        * `MSButton3`: Triggers the `setparcel` subroutine to select "Parcel" package type.
        * `MSButton4`: Triggers the `goroyalm` subroutine to start Royal Mail shipping.
        * `MSButton5`: Triggers the `Domessageclose` subroutine to close the dialog.
    * Handlers: Linked to their corresponding subroutines using `AddDialogHandler`.

* `Dialog9` (Warning):
    * Objects:
        * `MSButton1`: Triggers the `Domessageclose` subroutine to close the dialog.
    * Handlers: Linked to their corresponding subroutines using `AddDialogHandler`.

* `Dialog10` (Custom Invoice):
    * Objects:
        * `MSButton1`: Triggers the `Doinvoiceapply` subroutine to update the invoice data.
        * `MSButton2`: Triggers the `Doinvoiceclose` subroutine to close the dialog.
        * `MSButton3`: Triggers the `getotheritems` subroutine to combine invoices from multiple orders.
    * Handlers: Linked to their corresponding subroutines using `AddDialogHandler`.

* `Dialog11` (Info):
    * Objects: 
        * `MSButton1`: Triggers the `Domessageclose` subroutine to close the dialog.
    * Handlers: Linked to their corresponding subroutines using `AddDialogHandler`.

* `Dialog12` (EORI Check):
    * Objects:
        * `MSButton1`: Triggers the `DoEORIcheck` subroutine to check the EORI number.
        * `MSButton2`: Triggers the `DoApplyEORI` subroutine to apply the EORI number.
        * `MSButton3`: Triggers the `DoAbort` subroutine to abort the shipping process.
    * Handlers: Linked to their corresponding subroutines using `AddDialogHandler`.

* `Dialog13` (Shipping Note):
    * Objects:
        * `MSButton1-4`: Buttons to select the packer (e.g., `setwho1`, `setwho2`, etc.).
    * Handlers: Linked to their corresponding subroutines using `AddDialogHandler`.

* `Dialog14` (Order List):
    * Objects:
        * `MSButton1-23`: Buttons to select orders from the list. Each button triggers the `pickorderfromlist` subroutine with a different variable (e.g., `State1`, `State2`, etc.).
    * Handlers: Linked to their corresponding subroutines using `AddDialogHandler`.


2. Subroutines (`SRT>`):

* `pickorderfromlist(Var)`:
    * Description: Gets the selected order number from the order list window (`Dialog14`) and closes the window.
    * Input: `Var` (Variable containing the order number text).

* `showordersinlist`:
    * Description: Loads the list of orders into the order list window (`Dialog14`) and allows the user to select an order. This part is partially replaced with Python code (`python_getpickinglist`).
  
* `Doasanaissue`:
    * Description: Reports an issue to Asana through the Python script at the end of the code (`python_code_newsection`).
    * Input:  None (Takes input from the user through a dialog).

* `DoGO`:
    * Description: This is the main subroutine for automatic shipping. It calls the appropriate shipping subroutine based on the selected shipping service (e.g., `DoDPD3`, `DoFedEx3`, `DoUPS`, `DoRoyalMail`, etc.).
  
* `DoPart`:
    * Description: Flags the order as a partial shipment and calls the `DoGO` subroutine.
  
* `DoMANGO`:
    * Description:  This subroutine handles manual shipping. It retrieves data from the `Dialog6` window and calls the appropriate shipping subroutine.
  
* `DoPartMANGO`:
    * Description: Flags the order as a partial shipment and calls the `DoMANGO` subroutine.
  
* `setwho1-4`:
    * Description: Sets the packer's name (`whospacking` variable) based on the button clicked in the `Dialog13` window.
  
* `getwho`:
    * Description: Shows the `Dialog13` window to allow the user to select the packer.
  
* `DoScrape`:
    * Description: This subroutine retrieves order data from the API (or Magento) using the `Grabdata` subroutine. It then fills the main window with the retrieved information.
   
* `DoLogin`:
    * Description: This subroutine attempts to login to the Odoo admin page and opens the order details page.
  
* `Grabdata`:
    * Description:  Retrieves data from the API (or Magento) using the Python script at the end of the code (`python_odooapicode`). It then processes the data, performs checks, and fills the main window (`Dialog1`).
  
* `DoEORIcheck`:
    * Description: Checks the EORI number entered by the user using an external website.
  
* `DoApplyEORI`:
    * Description: Retrieves the EORI number from the `Dialog12` window and closes the window.
  
* `DoAbort`:
    * Description: Sets a flag to abort shipping and closes the `Dialog12` window.
  
* `getotheritems`:
    * Description: Combines invoice data from multiple orders.
   (Takes input from the user through a dialog).

* `filldialog`:
    * Description:  Fills the `Dialog1` window with the retrieved order data.
  
* `GetPostageData`:
    * Description:  Retrieves postage-related data and processes it, including character replacements and length checks.
  
* `Replace`:
    * Description: Replaces special characters in a text string based on a replacement list from the `replacecharfile`.
    * Input: `para1` (String containing the text to be replaced).
    * Output: `para1` (String with replaced characters).
* `Dolengthchange`:
    * Description: Updates relevant variables based on the user's changes in the `Dialog2` window.
  
* `Docountlines`:
    * Description: Counts the characters in the input fields of the `Dialog2` window.
  
* `Estpostage`:
    * Description:  Estimates the appropriate shipping service based on the order data and the postage configuration file.
   
* `Doinvoiceedit`:
    * Description:  Fills the invoice editing window (`Dialog10`) with items from the order.
  
* `Doinvoiceapply`:
    * Description: Updates invoice data based on the user's changes in the `Dialog10` window.
  
* `Doinvoiceclose`:
    * Description: Closes the `Dialog10` window.
  
* `Domessageclose`:
    * Description: Closes the `Dialog9` window.
  
* `DoDPD3`:
    * Description: Handles DPD shipping. Generates the DPD import file (`dpdinfile`) and writes data to the shipping schedule file (`schedulefile`).
  
* `DoUPS`:
    * Description: Handles UPS shipping. Generates the UPS import file (`upsinfile`) and writes data to the shipping schedule file (`schedulefile`).
  
* `Docollection`:
    * Description: Handles third-party collection shipments.  Generates a collection CSV file (`collectinfile`) and writes data to the shipping schedule file (`schedulefile`).
 
* `Setqueued`:
    * Description: Updates the order status to "Queued" in Odoo.
  
* `Setwaitingd`:
    * Description:  Updates the order status to "Awaiting Dispatch" in Odoo.
  
* `DoFedEx3`:
    * Description:  Handles FedEx shipping. Generates the FedEx import file (`fedexinfile`) and writes data to the shipping schedule file (`schedulefile`). 
  
* `setletter`, `setlletter`, `setparcel`:
    * Description:  Sets the Royal Mail package type (Letter, Large Letter, Parcel) based on the selected button in the `Dialog8` window.
  
* `goroyalm`:
    * Description: Shows the `Dialog8` window to allow the user to select a Royal Mail package type, and then calls the `DoRoyalMail` subroutine.
  
* `DoRoyalMail`:
    * Description:  Handles Royal Mail shipping. Generates the Royal Mail import file (`royalminfile`) and writes data to the shipping schedule file (`schedulefile`).
  
* `dialog6`:
    * Description: Opens the manual shipping dialog (`Dialog6`).
  
* `manualshipgrab`:
    * Description:  Retrieves shipping details from the main window (`Dialog1`) and populates the manual shipping dialog (`Dialog6`).
  

3. Python Code Integration

The MacroScheduler script uses Python code snippets (`PYExec`) for tasks like:

* `python_odooapicode`:  API call to Odoo (or Magento).
* `python_code_newsection`: Creating an Asana task.
* `python_donepicking`: Marking items as packed in Odoo.
* `python_getpickinglist`:  Retrieving a list of orders.
* `python_setstatus`: Setting the order status in Odoo.
* `python_addpackage`: Adding package dimensions.



