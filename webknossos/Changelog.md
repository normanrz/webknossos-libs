# Change Log

All notable changes to the webknossos python library are documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/) `MAJOR.MINOR.PATCH`.
For upgrade instructions, please check the respective *Breaking Changes* sections.

## Unreleased
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.9.5...HEAD)

### Breaking Changes

### Added
- Added `apply_merger_mode.py` example. [#592](https://github.com/scalableminds/webknossos-libs/pull/592)
- Added support for reading from multiple volume layers in annotations. If an annotation contains multiple volume layers, the layer name has to be provided when reading from a volume layer in an annotation (in `Annotation.save_volume_annotation()` and `Annotation.temporary_volume_annotation_layer_copy()`). Also, added the method `Annotation.get_volume_layer_names()` to see available volume layers. [#588](https://github.com/scalableminds/webknossos-libs/pull/588)

### Changed

### Fixed


## [0.9.5](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.9.5) - 2022-02-10
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.9.4...v0.9.5)

### Fixed
- Skeleton: Fixed a bug when comparing `Graph` instances, this fixes failing loads which had the error message `Can only compare wk.Graph to another wk.Graph.` before. [#593](https://github.com/scalableminds/webknossos-libs/pull/593)


## [0.9.4](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.9.4) - 2022-02-09
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.9.3...v0.9.4)

### Added
- Added AnnotationInfo, Project and Task classes for handling annotation information and annotation project administration. [#574](https://github.com/scalableminds/webknossos-libs/pull/574)

### Changed
- Lifted the restriction that `BoundingBox` cannot have a negative topleft (introduced in v0.9.0). Also, negative size dimensions are flipped, so that the topleft <= bottomright,
  e.g. `BoundingBox((10, 10, 10), (-5, 5, 5))` -> `BoundingBox((5, 10, 10), (5, 5, 5))`. [#589](https://github.com/scalableminds/webknossos-libs/pull/589)


## [0.9.3](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.9.3) - 2022-02-07
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.9.2...v0.9.3)

### Fixed
- `dataset.upload(layers_to_link=…)`: Fixed a bug where the upload did not complete if layers_to_link contained layers present in uploading dataset. [#584](https://github.com/scalableminds/webknossos-libs/pull/584)



## [0.9.2](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.9.2) - 2022-02-03
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.9.1...v0.9.2)

### Added
- A custom network request timeout can be set using `webknossos_context(…, timeout=300)` or `export WK_TIMEOUT="300"`. [#577](https://github.com/scalableminds/webknossos-libs/pull/577)

### Changed
- The default network request timeout changed from ½min to 30 min. [#577](https://github.com/scalableminds/webknossos-libs/pull/577)


## [0.9.1](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.9.1) - 2022-01-31
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.9.0...v0.9.1)

### Changed
- The signatures of `(Mag)View.for_each_chunk` and `(Mag)View.for_zipped_chunks` changed:
  * The previous argument `work_on_chunk` is now called `func_per_chunk`.
  * The various `chunk_size` arguments now have to be given in Mag(1). They now have default values.
- Deprecations in `(Mag)View.get_buffered_slice_reader/_writer` [#564](https://github.com/scalableminds/webknossos-libs/pull/564):
  * `(Mag)View.get_buffered_slice_reader`: using the parameters `offset` and `size` is deprecated.
    Please use the parameter relative_bounding_box or absolute_bounding_box (both in Mag(1)) instead.
    The old offset behavior was absolute for `MagView`s and relative for `View`s.
  * `(Mag)View.get_buffered_slice_writer`: using the parameter `offset` is deprecated.
    Please use the parameter relative_offset or absolute_offset (both in Mag(1)) instead.
    The old offset behavior was absolute for `MagView`s and relative for `View`s.


## [0.9.0](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.9.0) - 2022-01-19
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.8.31...v0.9.0)

### Breaking Changes
- Various changes in View & MagView signatures [#553](https://github.com/scalableminds/webknossos-libs/pull/553):
  - **Breaking Changes**:
    * `MagView.read`: if nothing is supplied and the layer does not start at (0, 0, 0),
      the default behaviour changes from starting at absolute (0, 0, 0) to the layer's bounding box
    * `MagView.write`: if no offset is supplied and the layer does not start at (0, 0, 0),
      the default behaviour changes from starting at absolute (0, 0, 0) to the layer's bounding box
    * `(Mag)View.get_view`: read_only is a keyword-only argument now
    * `MagView.get_bounding_boxes_on_disk()` now returns an iterator yielding bounding boxes in Mag(1)
    * `BoundingBox` cannot have negative topleft or size entries anymore (lifted in v0.9.4).
  - **Deprecations**
    The following usages are marked as deprecated with warnings and will be removed in future releases:
    * Using the `offset` parameter for `read`/`write`/`get_view` in MagView and View is deprecated.
      There are new counterparts `absolute_offset` and `relative_offset` which have to be specified in Mag(1),
      whereas `offset` previously was specified in the Mag of the respective View.
      Also, for `read`/`get_view` only using `size` is deprecated, since it used to refer to the size in the View's Mag.
      Instead, `size` should always be used together with `absolute_offset` or `relative_offset`. Then it is interpreted in Mag(1).
    * The (Mag)View attributes `view.global_offset` and `view.size` are deprecated now, which were in the Mag of the respective View.
      Please use `view.bounding_box` instead, which is in Mag(1).
    * `read_bbox` on the (Mag)View is deprecated as well, please use `read` with the `absolute_bounding_box`or `relative_bounding_box` parameter instead. You'll have to pass the bounding box in Mag(1) then.


### Added
- Added a check for dataset name availability before attempting to upload. [#555](https://github.com/scalableminds/webknossos-libs/pull/555)

### Fixed
- Fixed the dataset download of private datasets which need a token. [#562](https://github.com/scalableminds/webknossos-libs/pull/562)



## [0.8.31](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.8.31) - 2022-01-07
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.8.30...v0.8.31)

### Added
- Added `Annotation.save("file_name")` to save an annotation to a file and `Annotation.temporary_volume_annotation_layer_copy()` to read from the volume layer of an annotation as a WK dataset. [#528](https://github.com/scalableminds/webknossos-libs/pull/528)
- Added `layers_to_link` parameter to `Dataset.upload()` so that layers don't need to be uploaded again if they already exist in another dataset on webKnossos. [#544](https://github.com/scalableminds/webknossos-libs/pull/544)


## [0.8.30](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.8.30) - 2021-12-27
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.8.29...v0.8.30)

### Breaking Changes
- The BoundingBoxNamedTuple was removed. Use BoundingBox instead. [#526](https://github.com/scalableminds/webknossos-libs/pull/526)
- Some methods of creating, opening and saving have changed. The old methods are still available but deprecated. [The documentation gives a good overview](https://docs.webknossos.org/api/webknossos.html). Specifically, the changes are :
  * `Dataset.create()` → `Dataset()`
  * `Dataset.get_or_create()` → `Dataset(…, exist_ok=True)`
  * `Dataset()` → `Dataset.open()`
  * `download_dataset()` → `Dataset.download()`
  * `open_annotation()` → `Annotation.load()` for local files, `Annotation.download()` to download from webKnossos
  * `open_nml()` → `Skeleton.load()`
  * `Skeleton.from_path()` → `Skeleton.load()`
  * `Skeleton.write()` → `Skeleton.save()`
  The deprecated methods will be removed in future releases.
  [#520](https://github.com/scalableminds/webknossos-libs/pull/520)

### Changed
- The detailed output of e.g. downsampling was replaced with a progress bar. [#527](https://github.com/scalableminds/webknossos-libs/pull/527)
- Always use the sampling mode `CONSTANT_Z` when downsampling 2D data. [#516](https://github.com/scalableminds/webknossos-libs/pull/516)
- Make computation of `largestSegmentId` more efficient for volume annotations. [#531](https://github.com/scalableminds/webknossos-libs/pull/531)
- Consistently use resolved instead of absolute path if make_relative is False. [#536](https://github.com/scalableminds/webknossos-libs/pull/536)


## [0.8.29](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.8.29) - 2021-12-14
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.8.28...v0.8.29)

### Breaking Changes
- To download datasets, a recent webknossos server version is necessary (>= 21.12.0). webknossos.org is unaffected. [#510](https://github.com/scalableminds/webknossos-libs/pull/510)


## [0.8.28](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.8.28) - 2021-12-09
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.8.27...v0.8.28)


## [0.8.27](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.8.27) - 2021-12-09
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.8.25...v0.8.27)


## [v0.8.25](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.8.25) - 2021-12-07
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.8.24...v0.8.25)

### Added
- Added support to download datasets from external datastores, which is the case for webknossos.org. [#497](https://github.com/scalableminds/webknossos-libs/pull/497)

### Changed
- Adapt the dataset upload to new webKnossos api. [#484](https://github.com/scalableminds/webknossos-libs/pull/484)
- `get_segmentation_layer()` and `get_color_layer()` were deprecated and should not be used, anymore, as they will fail if no or more than one layer exists for each category. Instead, `get_segmentation_layers()` and `get_color_layers()` should be used (if desired in combination with `[0]` to get the old, error-prone behavior).
- Renamed the folder webknossos/script-collection to webknossos/script_collection to enable module imports. [#505](https://github.com/scalableminds/webknossos-libs/pull/505)

## [v0.8.24](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.8.24) - 2021-11-30
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.8.23...v0.8.24)


## [v0.8.23](https://github.com/scalableminds/webknossos-libs/releases/tag/v0.8.23) - 2021-11-29
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.8.22...v0.8.23)

### Breaking Changes
- `wk.Graph` now inherits from `networkx.Graph` directly. Therefore, the `nx_graph` attribute is removed. [#481](https://github.com/scalableminds/webknossos-libs/pull/481)
- The class `LayerCategories` was removed. `COLOR_TYPE` and `SEGMENTATION_TYPE` were renamed to `COLOR_CATEGORY` and `SEGMENTATION_CATEGORY` and can now be imported directly. The type of many parameters were changed from `str` to the literal `LayerCategoryType`. [#454](https://github.com/scalableminds/webknossos-libs/pull/454)

### Added
- Added `redownsample()` method to `Layer` to recompute existing downsampled magnifications. [#461](https://github.com/scalableminds/webknossos-libs/pull/461)
- Added `globalize_floodfill.py` script to globalize partially computed flood fill operations. [#461](https://github.com/scalableminds/webknossos-libs/pull/461)

### Changed
- Improved performance for calculations with `Vec3Int` and `BoundingBox`. [#461](https://github.com/scalableminds/webknossos-libs/pull/461)

### Fixed
- Resolve path when symlinking layer and make_relative is False (instead of only making it absolute). [#492](https://github.com/scalableminds/webknossos-libs/pull/492)


## [0.8.22](https://github.com/scalableminds/webknossos-cuber/releases/tag/v0.8.22) - 2021-11-01
[Commits](https://github.com/scalableminds/webknossos-cuber/compare/v0.8.21...v0.8.22)

### Breaking Changes
- Removed the `organization` parameter from the `webknossos_context` function. The organization will automatically be fetched using the token of the user. [#470](https://github.com/scalableminds/webknossos-libs/pull/470)

### Fixed
- Make Views picklable. We now ignore the file handle when we pickle Views. [#469](https://github.com/scalableminds/webknossos-libs/pull/469)

## [v0.8.19](https://github.com/scalableminds/webknossos-cuber/releases/tag/v0.8.19) - 2021-10-21
[Commits](https://github.com/scalableminds/webknossos-libs/compare/v0.8.18...v.8.19)
### Added
- Added a `User` class to the client that can be used to get meta-information of users or their logged time. The currently logged in user can be accessed, as well as all managed users. [#470](https://github.com/scalableminds/webknossos-libs/pull/470)


## [0.8.21](https://github.com/scalableminds/webknossos-cuber/releases/tag/v0.8.21) - 2021-10-28
[Commits](https://github.com/scalableminds/webknossos-cuber/compare/v0.8.20...v0.8.21)

### Changed
- Downgraded typing-extensions for better dependency compatibility  [#472](https://github.com/scalableminds/webknossos-libs/pull/472)


## [0.8.20](https://github.com/scalableminds/webknossos-cuber/releases/tag/v0.8.20) - 2021-10-28
[Commits](https://github.com/scalableminds/webknossos-cuber/compare/v0.8.19...v0.8.20)

### Breaking Changes
- `BoundingBox.chunk()`'s 2nd parameter `chunk_border_alignments` now does not accept a list with a single `int` anymore. [#452](https://github.com/scalableminds/webknossos-libs/pull/452)

### Fixed
- Make Views picklable. We now ignore the file handle when we pickle Views. [#469](https://github.com/scalableminds/webknossos-libs/pull/469)


## [0.8.19](https://github.com/scalableminds/webknossos-cuber/releases/tag/v0.8.19) - 2021-10-21
[Commits](https://github.com/scalableminds/webknossos-cuber/compare/v0.8.18...v0.8.19)

### Breaking Changes
- `View`s now always open the `wkw.Dataset` lazily. All explicit calls to `View.open()` and `View.close()` must be removed. [#448](https://github.com/scalableminds/webknossos-libs/pull/448)
-
### Added
- Added a new Annotation class which includes skeletons as well as volume-annotations. [#452](https://github.com/scalableminds/webknossos-libs/pull/452)
- Added dataset down- and upload as well as annotation download, see the examples `learned_segmenter.py` and `upload_image_data.py`. [#452](https://github.com/scalableminds/webknossos-libs/pull/452)


## [0.8.18](https://github.com/scalableminds/webknossos-cuber/releases/tag/v0.8.18) - 2021-10-18
[Commits](https://github.com/scalableminds/webknossos-cuber/compare/v0.8.16...v0.8.18)

### Added
- The Dataset class now has a new method: add_shallow_copy. [#437](https://github.com/scalableminds/webknossos-libs/pull/437)
### Changed
- The `Vec3Int` constructor now asserts that its components are whole numbers also in numpy case. [#434](https://github.com/scalableminds/webknossos-libs/pull/434)
- Updated scikit-image dependency to 0.18.3. [#435](https://github.com/scalableminds/webknossos-libs/pull/435)
- `BoundingBox.contains` now also takes float points in numpy arrays. [#450](https://github.com/scalableminds/webknossos-libs/pull/450)
### Fixed

## [0.8.16](https://github.com/scalableminds/webknossos-cuber/releases/tag/v0.8.16) - 2021-09-22
[Commits](https://github.com/scalableminds/webknossos-cuber/compare/v0.8.15...v0.8.16)

### Breaking Changes
- Refactored the BufferedSliceWriter and added a BufferedSliceReader. [#425](https://github.com/scalableminds/webknossos-libs/pull/425)
  - BufferedSliceWriter
    - The data no longer gets transposed: previously the format of the slices was [y,x]; now it is [x,y]
    - The interface of the constructor was changed:
      - A `View` (or `MagView`) is now required as datasource
      - The parameter `dimension` can be used to specify the axis along the data is sliced
      - The offset is expected to be in the magnification of the view
    - This class is now supposed to be used within a context manager and the slices are written by sending them to the generator (see documentation of the class).
  - BufferedSliceReader
    - This class was added complementary to the BufferedSliceWriter
  - Added methods to get a BufferedSliceReader/BufferedSliceWriter from a View directly

### Added
### Changed
### Fixed

## [0.8.15](https://github.com/scalableminds/webknossos-cuber/releases/tag/v0.8.15) - 2021-09-22
[Commits](https://github.com/scalableminds/webknossos-cuber/compare/v0.8.13...v0.8.15)

### Breaking Changes

- Breaking changes were introduced for geometry classes in [#421](https://github.com/scalableminds/webknossos-libs/pull/421):
  - `BoundingBox`
    - is now immutable, use convenience methods, e.g. `bb.with_topleft((0,0,0))`
    - properties topleft and size are now Vec3Int instead of np.array, they are each immutable as well
    - all `to_`-conversions return a copy, some were renamed:
    - `to_array` → `to_list`
    - `as_np` → `to_np`
    - `as_wkw` → `to_wkw_dict`
    - `from_wkw` → `from_wkw_dict`
    - `as_config` → `to_config_dict`
    - `as_checkpoint_name` → `to_checkpoint_name`
    - `as_tuple6` → `to_tuple6`
    - `as_csv` → `to_csv`
    - `as_named_tuple` → `to_named_tuple`
    - `as_slices` → `to_slices`
    - `copy` → (gone, immutable)

  - `Mag`
    - is now immutable
    - `mag.mag` is now `mag._mag` (considered private, use to_list instead if you really need it as list)
    - all `to_`-conversions return a copy, some were renamed:
    - `to_array` → `to_list`
    - `scale_by` → (gone, immutable)
    - `divide_by` → (gone, immutable)
    - `as_np` → `to_np`

### Added

 - An immutable Vec3Int class was introduced that holds three integers and provides a number of convenience methods and accessors. [#421](https://github.com/scalableminds/webknossos-libs/pull/421)

### Changed

- `BoundingBox` and `Mag` are now immutable attr classes containing `Vec3Int` values. See breaking changes above.

### Fixed

-

## [0.8.13](https://github.com/scalableminds/webknossos-cuber/releases/tag/v0.8.13) - 2021-09-22
[Commits](https://github.com/scalableminds/webknossos-cuber/compare/v0.8.12...v0.8.13)

This is the latest release at the time of creating this changelog.
