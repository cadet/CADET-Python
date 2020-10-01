import cadet

data = cadet.H5()
data.filename = r"F:\MCMC\Synthetic\Bypass\Bypass_MCMC_pump_delay\mcmc_refine\mcmc\mcmc.h5"
data.load(paths=["/bounds_change/json",])


print(data)

print("bounds json", data.root.bounds_change)


print("json", data.root.bounds_change.json)



data.load(paths=["/bounds_change",])



print("bounds_change", data)



data.load()



print("all", data)