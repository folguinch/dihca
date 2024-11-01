import admit
sources = ['16h30m58.761s', '-48d43m54.01s', '16h30m58.703s', '-48d43m52.60s',
        '16h30m58.631s', '-48d43m51.28s', '16h30m58.676s', '-48d43m51.78s',
        '16h30m58.889s', '-48d43m55.18s']
for spw in range(4):
    # Spw 
    p = admit.Project('results/G335.579-0.272.config5.spw%i.admit' % spw, dataserver=True)
    # Flow tasks.
    t0  = p.addtask(admit.Ingest_AT(file='clean/G335.579-0.272.config5.spw%i.fits' % spw, 
        vlsr=-46.3, edge=[10], box=[414,423,555,561]))
    t1  = p.addtask(admit.CubeStats_AT(ppp=True), [t0])
    t3  = p.addtask(admit.CubeSpectrum_AT(pos=sources), [t0])
    t4  = p.addtask(admit.LineID_AT(csub=[0, 0], minchan=4, maxgap=6,
        numsigma=5.0, allowexotics=True), [t1, t3])
    p.run()

# Source specific
for spw in range(4):
    # Spw 
    p = admit.Project('results/G335.579-0.272.config5.spw%i.bysource.admit' % spw, dataserver=True)
    # Flow tasks.
    t0  = p.addtask(admit.Ingest_AT(file='clean/G335.579-0.272.config5.spw%i.fits' % spw, 
        vlsr=-46.3, edge=[10], box=[414,423,555,561]))
    t3  = p.addtask(admit.CubeSpectrum_AT(pos=sources[:2]), [t0])
    t4  = p.addtask(admit.LineID_AT(csub=[0, 0], minchan=4, maxgap=6,
        numsigma=5.0, allowexotics=True), [t3])
    t5  = p.addtask(admit.CubeSpectrum_AT(pos=sources[2:4]), [t0])
    t6  = p.addtask(admit.LineID_AT(csub=[0, 0], minchan=4, maxgap=6,
        numsigma=5.0, allowexotics=True), [t5])
    t7  = p.addtask(admit.CubeSpectrum_AT(pos=sources[4:6]), [t0])
    t8  = p.addtask(admit.LineID_AT(csub=[0, 0], minchan=4, maxgap=6,
        numsigma=5.0, allowexotics=True), [t7])
    t9  = p.addtask(admit.CubeSpectrum_AT(pos=sources[6:8]), [t0])
    t10 = p.addtask(admit.LineID_AT(csub=[0, 0], minchan=4, maxgap=6,
        numsigma=5.0, allowexotics=True), [t9])
    t11 = p.addtask(admit.CubeSpectrum_AT(pos=sources[8:]), [t0])
    t12 = p.addtask(admit.LineID_AT(csub=[0, 0], minchan=4, maxgap=6,
        numsigma=5.0, allowexotics=True), [t11])
    p.run()
