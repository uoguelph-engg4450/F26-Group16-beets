// Use case diagram for the Assignment 2 shortlist (beets change requests).
// Run with ../build.sh; it creates beets-a2-usecases.asta and exports the PNG.
var TM = Java.type('com.change_vision.jude.api.inf.editor.TransactionManager');
var Point = Java.type('java.awt.geom.Point2D.Double');
var project = astah.getProject();
var basic = astah.getModelEditorFactory().getBasicModelEditor();
var ucm = astah.getModelEditorFactory().getUseCaseModelEditor();
var ucd = astah.getDiagramEditorFactory().getUseCaseDiagramEditor();

var SELECTED = '#C6EFCE', BACKUP = '#FFE7B3', SHORTLIST = '#FFFFCC', DROPPED = '#E7E7E7';

TM.beginTransaction();
try {
  var pkg = basic.createPackage(project, 'beets change requests');
  var diagram = ucd.createUseCaseDiagram(pkg, 'UC1 beets change requests');
  ucd.setDiagram(diagram);

  // system boundary and legend
  var boundary = ucd.createRect(new Point(200, 70), 1000, 930);
  boundary.setProperty('fill.color', '#FFFFFF');
  ucd.createText('beets (music library manager)', new Point(215, 80));
  ucd.createText('UC1  Use cases of the shortlisted change requests (issue numbers from github.com/beetbox/beets)', new Point(30, 20));
  ucd.createText('Green: selected for implementation.  Orange: backup.  Yellow: shortlisted, not selected.  Grey: not reproducible or already fixed in beets 2.14.1.', new Point(30, 40));

  // actors: the user on the left, the external services on the right, each level with its use case
  function actor(name, x, y) { var a = ucm.createActor(pkg, name); return ucd.createNodePresentation(a, new Point(x, y)); }
  var userModel = ucm.createActor(pkg, 'Music collector');
  var user = ucd.createNodePresentation(userModel, new Point(70, 300));
  var user2 = ucd.createNodePresentation(userModel, new Point(70, 780));  // the same actor, level with the lower use cases
  var mbModel = ucm.createActor(pkg, 'MusicBrainz');
  var mb = ucd.createNodePresentation(mbModel, new Point(1270, 60));
  var tidal = actor('Tidal', 1270, 175);
  var lrclib = actor('LRCLIB lyrics service', 1270, 290);
  var art = actor('Album art sources', 1270, 420);
  var mb2 = ucd.createNodePresentation(mbModel, new Point(1270, 840));  // the same actor, shown again near Submit

  // use cases: the user's goals in the left column, what they include or are extended by on the right
  function uc(name, x, y, fill) {
    var u = ucm.createUseCase(pkg, name);
    var p = ucd.createNodePresentation(u, new Point(x, y));
    p.setProperty('fill.color', fill);
    return p;
  }
  var importMusic = uc('Import music', 280, 130, SHORTLIST);
  var lyrics = uc('Fetch synced lyrics (#7070)', 280, 300, SELECTED);
  var embed = uc('Embed album art at configured quality (#5937)', 280, 530, SELECTED);
  var modify = uc('Modify metadata', 280, 650, SHORTLIST);
  var exportData = uc('Export selected fields (#5411)', 280, 750, BACKUP);
  var complete = uc('Complete commands in the shell (#2836)', 280, 840, DROPPED);
  var submit = uc('Submit release to MusicBrainz', 280, 930, SHORTLIST);
  var findRelease = uc('Find matching release (#6770 Tidal search limit)', 720, 120, SHORTLIST);
  var fetchArt = uc('Fetch album art', 820, 440, SHORTLIST);
  var review = uc('Review and select changes (#7019)', 760, 650, DROPPED);
  var tracklist = uc('Print track list in disc order (#4061)', 760, 945, SHORTLIST);

  function link(model, a, b) { return ucd.createLinkPresentation(model, a, b); }
  function assoc(a, b) { link(basic.createAssociation(a.getModel(), b.getModel(), '', '', ''), a, b); }
  function include(base, inc) { link(ucm.createInclude(base.getModel(), inc.getModel(), ''), base, inc); }
  function extend(extension, base) { link(ucm.createExtend(extension.getModel(), base.getModel(), ''), extension, base); }

  // the user's goals
  assoc(user, importMusic);
  assoc(user, lyrics);
  assoc(user, embed);
  assoc(user2, modify);
  assoc(user2, exportData);
  assoc(user2, submit);
  assoc(user2, complete);
  // external systems
  assoc(findRelease, mb);
  assoc(findRelease, tidal);
  assoc(lyrics, lrclib);
  assoc(fetchArt, art);
  assoc(submit, mb2);
  // structure
  include(importMusic, findRelease);
  extend(lyrics, importMusic);
  extend(fetchArt, importMusic);
  extend(embed, fetchArt);
  include(modify, review);
  include(submit, tracklist);

  TM.endTransaction();
  print('USE CASE DIAGRAM DONE');
} catch (e) { if (TM.isInTransaction()) TM.abortTransaction(); print('USE CASE DIAGRAM FAILED: ' + e); throw e; }
