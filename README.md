# Single and Multi Objective Optimization in Python - a Desktop Application

This project aimed at creating a friendly **Graphical User Interface** for Single and Multi Objective Optimization in python, over the established optimization library, **pymoo** (https://pymoo.org/index.html). It was done in light of the Master Thesis Dissertation by Tomás Líbano Monteiro in Universidade de Lisboa - Instituto Superior Técnico.

It provides an interface capable of running multiple Algorithms on multiple Problems with a single click of a button. The results can be presented through multiple performance indicators, and various visualization techniques. 

## Installation

1. If you do not have git installed, download the zip file from this repository ([https://github.com/tomaslibanomonteiro/Thesis-code](https://github.com/tomaslibanomonteiro/Thesis-code)) and extract it to a directory of your choice. Otherwise, issue the command to clone the project repository to your local machine.

    ```bash
    $ git clone https://github.com/tomaslibanomonteiro/Thesis-code
    ```

2. Although not required, it is recommended to create a virtual environment for the installation of the project dependencies. Installing a package manager such as Anaconda [https://www.anaconda.com/download](https://www.anaconda.com/download) can facilitate this process. To create a new environment with python 3.9 through conda, execute the command below.

    ```bash
    $ conda create -n my_env python=3.9
    ```

3. Navigate to the project directory and activate the environment.

    ```bash
    $ conda activate my_env 
    ```

4. Install the required dependencies using the `utils/requirements.txt` file of the project. 

    ```bash
    $ pip install -r utils/requirements.txt 
    ```

5. Run the `main.py` file to start the application.

    ```bash
    $ python main.py 
    ```

## Integration of personalized code

Add your class and correspondent string ID to the 'backend/get.py' file, in the respective 'get' function. The class is now going to appear in the app. For more instructions, read the corresponding chapter in the Thesis document in the 'thesis' folder. 

## Contributions
The project was only done for academic and educational purposes. Any further development is encourage under the License's Terms and Conditions. You can contact me at tomas.libano.monteiro@tecnico.ulisboa.pt

## License

MIT