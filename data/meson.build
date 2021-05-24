# Initialize a local variable to hold an installation path.
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

gnome = import('gnome')

resources = gnome.compile_resources(
  'purism-cv',
  'purism-cv.gresource.xml',
  gresource_bundle: true,
  source_dir: meson.current_build_dir(),
  install: true,
  install_dir: get_option('datadir') / meson.project_name(),
)

desktop_file = i18n.merge_file(
  input: 'com.github.wctaylor.PurismCV.desktop.in',
  output: 'com.github.wctaylor.PurismCV.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

appstream_file = i18n.merge_file(
  input: 'com.github.wctaylor.PurismCV.appdata.xml.in',
  output: 'com.github.wctaylor.PurismCV.appdata.xml',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'appdata')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util,
    args: ['validate', appstream_file]
  )
endif

install_data('com.github.wctaylor.PurismCV.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif

subdir('icons')

# Install file to application-specific locations
install_data ('profile.json',
  install_dir: pkgdatadir)

# Install images to application-specific locations.
install_subdir('images',
  install_dir: pkgdatadir
)

