def exponential():
    num = int(input ("Enter number to exponentiate:") )
    n = int(input ("Enter how many times to double: "))
    while n != 0:
        num = num * 2
        n -= 1
    print ("Answer: " + str(num))
    return num

def main():
     exponential()

if __name__== "__main__":
  main()