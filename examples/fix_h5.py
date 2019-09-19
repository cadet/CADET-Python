from cadet import Cadet

fix = Cadet()
fix.filename = r"F:\output\dextran\dextran_pulse.h5"
fix.load()
fix.root.input.model.unit_001.adsorption_model = "LINEAR"
fix.root.input.model.unit_001.adsorption.is_kinetic = 1
fix.root.input.model.unit_001.adsorption.lin_ka = [0.0]
fix.root.input.model.unit_001.adsorption.lin_kd = [1e3]
fix.save()