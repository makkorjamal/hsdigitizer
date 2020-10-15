def adder(**args):
    sum = 0
    for key, value in args.items():
        print('{} {}'.format(key, value))
adder(name='jamal', surname='makkor', age=32)
