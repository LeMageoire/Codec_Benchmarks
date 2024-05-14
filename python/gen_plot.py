def gen_plots(result):
    """
    Generate the plots for the benchmark
    the results should holds :
    - the error rate for each iteration
    - the ratio of success for each iteration (decoded 100% correctly)
    - the time of execution for each iteration (average of the N iterations)

    - for each N simulations aggregated we should have two plots :
        - one with constant error rate showing the ratio of success for each package_repetition variation
        - one with constant package_repetition showing the ratio of success for each error rate variation
    
    :result: the result of the benchmark
    """

    # create 2 subplots with a global name of benchmark (for the title)
    fig, axs = plt.subplots(2)
    fig.suptitle("benchmark_name")
    # for the first subplot we have to plot the error rate for each iteration

    # for the second subplot we have to plot the ratio of success for each iteration
    