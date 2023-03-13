from input.input import Input
from run.run import Run

def main():
    input = Input('input.csv')
    run = Run(input)
    run.data.to_csv('output.csv', index=False)
    
if __name__ == '__main__':
    main()


