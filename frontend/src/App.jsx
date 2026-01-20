import { useState } from 'react'

// Icon Components
const UploadIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
  </svg>
)

const DownloadIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
  </svg>
)

const CheckIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
)

const XIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
)

const LoadingSpinner = () => (
  <div className="flex justify-center items-center">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
  </div>
)

const FolderIcon = ({ isOpen }) => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    {isOpen ? (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
    ) : (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
    )}
  </svg>
)

const ChevronIcon = ({ isOpen }) => (
  <svg 
    className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-90' : ''}`} 
    fill="none" 
    stroke="currentColor" 
    viewBox="0 0 24 24"
  >
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
)

const FileIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
)

// Folder Tree Component
const FolderTree = ({ title, files, duplicateUsernames, keptUsernames, source }) => {
  // Build folder structure
  const folderStructure = {}
  files.forEach(file => {
    const folder = file.folder || 'root'
    if (!folderStructure[folder]) {
      folderStructure[folder] = []
    }
    folderStructure[folder].push(file)
  })

  // Initialize all folders as expanded by default
  const initialExpandedState = {}
  Object.keys(folderStructure).forEach(folder => {
    initialExpandedState[folder] = true
  })
  
  const [expandedFolders, setExpandedFolders] = useState(initialExpandedState)

  const toggleFolder = (folder) => {
    setExpandedFolders(prev => ({
      ...prev,
      [folder]: !prev[folder]
    }))
  }

  const isKept = (username) => keptUsernames.includes(username)
  const isRemoved = (username) => duplicateUsernames.includes(username) && !isKept(username)

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <FolderIcon isOpen={true} />
        {title}
      </h3>
      
      <div className="space-y-1">
        {Object.entries(folderStructure).map(([folder, folderFiles]) => {
          const isExpanded = expandedFolders[folder] ?? true
          const keptCount = folderFiles.filter(f => isKept(f.username)).length
          const removedCount = folderFiles.filter(f => isRemoved(f.username)).length
          const totalCount = folderFiles.length

          return (
            <div key={folder} className="border-l-2 border-gray-200 pl-4">
              {/* Folder Header */}
              <button
                onClick={() => toggleFolder(folder)}
                className="w-full flex items-center gap-2 py-2 px-2 hover:bg-gray-50 rounded transition-colors text-left"
              >
                <ChevronIcon isOpen={isExpanded} />
                <FolderIcon isOpen={isExpanded} />
                <span className="font-semibold text-gray-700 flex-1">{folder}</span>
                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                  {totalCount} file{totalCount !== 1 ? 's' : ''}
                  {keptCount > 0 && (
                    <span className="ml-2 text-green-600">
                      <span className="w-2 h-2 bg-green-500 rounded-full inline-block mr-1"></span>
                      {keptCount} kept
                    </span>
                  )}
                  {removedCount > 0 && (
                    <span className="ml-2 text-red-600">
                      <span className="w-2 h-2 bg-red-500 rounded-full inline-block mr-1"></span>
                      {removedCount} removed
                    </span>
                  )}
                </span>
              </button>

              {/* Folder Contents */}
              {isExpanded && (
                <div className="ml-6 space-y-1 mt-1">
                  {folderFiles.map((file, index) => {
                    const kept = isKept(file.username)
                    const removed = isRemoved(file.username)

                    return (
                      <div
                        key={index}
                        className={`flex items-center gap-2 py-1.5 px-2 rounded ${
                          removed ? 'bg-red-50 opacity-75' : kept ? 'bg-green-50' : 'hover:bg-gray-50'
                        }`}
                      >
                        <FileIcon />
                        <span
                          className={`flex-1 text-sm ${
                            removed ? 'line-through text-red-600' : 'text-gray-700'
                          }`}
                        >
                          {file.filename}
                        </span>
                        <span className="text-xs font-medium text-gray-500">
                          ({file.username})
                        </span>
                        {kept && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                            Kept
                          </span>
                        )}
                        {removed && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                            Removed
                          </span>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function App() {
  const [file1, setFile1] = useState(null)
  const [file2, setFile2] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState(null)

  const handleFile1Change = (e) => {
    const file = e.target.files[0]
    if (file) {
      if (!file.name.toLowerCase().endsWith('.zip')) {
        setError('File 1 must be a ZIP file')
        setFile1(null)
        return
      }
      setFile1(file)
      setError('')
    }
  }

  const handleFile2Change = (e) => {
    const file = e.target.files[0]
    if (file) {
      if (!file.name.toLowerCase().endsWith('.zip')) {
        setError('File 2 must be a ZIP file')
        setFile2(null)
        return
      }
      setFile2(file)
      setError('')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setSummary(null)
    setLoading(true)

    if (!file1 || !file2) {
      setError('Please select both ZIP files')
      setLoading(false)
      return
    }

    if (!file1.name.toLowerCase().endsWith('.zip') || !file2.name.toLowerCase().endsWith('.zip')) {
      setError('Both files must be ZIP files')
      setLoading(false)
      return
    }

    try {
      const formData = new FormData()
      formData.append('file1', file1)
      formData.append('file2', file2)

      const response = await fetch('/api/compare-zips', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error occurred' }))
        setError(errorData.detail || `Error: ${response.statusText}`)
        setLoading(false)
        return
      }

      const data = await response.json()
      
      const binaryString = atob(data.zip_file)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
      const blob = new Blob([bytes], { type: 'application/zip' })
      
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = data.filename || 'result.zip'
      document.body.appendChild(a)
      a.click()
      
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      setSummary(data.summary)
      const stats = data.summary.summary_stats
      setSuccess(`Files processed successfully! Found ${data.summary.zip1_stats.total_files} files in ZIP 1, ${data.summary.zip2_stats.total_files} files in ZIP 2. ${stats.total_duplicates} duplicates detected. Final merged ZIP contains ${stats.total_kept} files.`)
      setLoading(false)
    } catch (err) {
      setError(`Error: ${err.message}`)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-3">
            ZIP Comparison Tool
          </h1>
          <p className="text-lg text-gray-600">
            Upload two ZIP files to merge and compare PDFs by username
          </p>
        </div>

        {/* Upload Card */}
        <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8 mb-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* File 1 Upload */}
            <div className="space-y-2">
              <label htmlFor="file1" className="block text-sm font-semibold text-gray-700">
                ZIP File 1
              </label>
              <p className="text-xs text-gray-500 mb-3">
                Contains folders with PDFs named USERNAME_CODE.pdf
              </p>
              <div className="relative">
                <input
                  type="file"
                  id="file1"
                  accept=".zip"
                  onChange={handleFile1Change}
                  className="hidden"
                  disabled={loading}
                />
                <label
                  htmlFor="file1"
                  className={`flex items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-all ${
                    file1
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50'
                  } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <div className="flex flex-col items-center">
                    <UploadIcon />
                    <span className="mt-2 text-sm text-gray-600">
                      {file1 ? file1.name : 'Click to upload ZIP file'}
                    </span>
                    {file1 && (
                      <span className="mt-1 text-xs text-green-600 font-medium flex items-center gap-1">
                        <CheckIcon />
                        File selected
                      </span>
                    )}
                  </div>
                </label>
              </div>
            </div>

            {/* File 2 Upload */}
            <div className="space-y-2">
              <label htmlFor="file2" className="block text-sm font-semibold text-gray-700">
                ZIP File 2
              </label>
              <p className="text-xs text-gray-500 mb-3">
                Contains folders named USERNAME(NUMBER) NAME with PDFs
              </p>
              <div className="relative">
                <input
                  type="file"
                  id="file2"
                  accept=".zip"
                  onChange={handleFile2Change}
                  className="hidden"
                  disabled={loading}
                />
                <label
                  htmlFor="file2"
                  className={`flex items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-all ${
                    file2
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50'
                  } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <div className="flex flex-col items-center">
                    <UploadIcon />
                    <span className="mt-2 text-sm text-gray-600">
                      {file2 ? file2.name : 'Click to upload ZIP file'}
                    </span>
                    {file2 && (
                      <span className="mt-1 text-xs text-green-600 font-medium flex items-center gap-1">
                        <CheckIcon />
                        File selected
                      </span>
                    )}
                  </div>
                </label>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !file1 || !file2}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold py-3 px-6 rounded-xl shadow-lg hover:from-blue-700 hover:to-indigo-700 transform hover:scale-[1.02] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <LoadingSpinner />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <UploadIcon />
                  <span>Upload & Process</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg mb-6">
            <div className="flex items-center gap-2">
              <XIcon />
              <div>
                <p className="font-semibold text-red-800">Error</p>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg mb-6">
            <div className="flex items-center gap-2">
              <CheckIcon />
      <div>
                <p className="font-semibold text-green-800">Success</p>
                <p className="text-green-700 text-sm">{success}</p>
              </div>
            </div>
          </div>
        )}

        {/* Summary Section */}
        {summary && (() => {
          // Calculate kept and removed usernames
          const keptUsernames = summary.final_merged.files.map(f => f.username)
          const duplicateUsernames = summary.duplicate_pairs.map(p => p.username)
          const zip1RemovedUsernames = summary.zip1_stats.files
            .filter(f => f.status === 'duplicate' && !keptUsernames.includes(f.username))
            .map(f => f.username)
          const zip2RemovedUsernames = summary.zip2_stats.files
            .filter(f => !f.kept)
            .map(f => f.username)

          return (
            <div className="space-y-6">
              {/* Statistics Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl p-6 shadow-lg">
                  <div className="text-4xl font-bold mb-2">{summary.zip1_stats.total_files}</div>
                  <div className="text-sm font-medium opacity-90 mb-1">Files in ZIP 1</div>
                  <div className="text-xs opacity-75">
                    {summary.zip1_stats.unique_files} unique, {summary.zip1_stats.duplicate_files} duplicates
                  </div>
                </div>
                <div className="bg-gradient-to-br from-pink-500 to-rose-600 text-white rounded-xl p-6 shadow-lg">
                  <div className="text-4xl font-bold mb-2">{summary.zip2_stats.total_files}</div>
                  <div className="text-sm font-medium opacity-90 mb-1">Files in ZIP 2</div>
                  <div className="text-xs opacity-75">
                    {summary.zip2_stats.unique_files} unique, {summary.zip2_stats.duplicate_files} duplicates
                  </div>
                </div>
                <div className="bg-gradient-to-br from-emerald-500 to-teal-600 text-white rounded-xl p-6 shadow-lg">
                  <div className="text-4xl font-bold mb-2">{summary.final_merged.total_files}</div>
                  <div className="text-sm font-medium opacity-90 mb-1">Final Merged Files</div>
                  <div className="text-xs opacity-75">
                    {summary.summary_stats.total_duplicates} duplicates removed
                  </div>
                </div>
              </div>

              {/* Folder Structure View */}
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Folder Structure</h2>
                
                <FolderTree
                  title="ZIP File 1"
                  files={summary.zip1_stats.files}
                  duplicateUsernames={duplicateUsernames.filter(u => keptUsernames.includes(u))}
                  keptUsernames={keptUsernames}
                  source="ZIP File 1"
                />

                <FolderTree
                  title="ZIP File 2"
                  files={summary.zip2_stats.files}
                  duplicateUsernames={zip2RemovedUsernames}
                  keptUsernames={keptUsernames}
                  source="ZIP File 2"
                />
              </div>

            {/* ZIP File 1 Details */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">
                ZIP File 1 - All Files ({summary.zip1_stats.total_files} files)
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Username</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Folder</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Filename</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Status</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {summary.zip1_stats.files.map((file, index) => (
                      <tr key={index} className={file.status === 'duplicate' ? 'bg-yellow-50' : 'hover:bg-gray-50'}>
                        <td className="px-4 py-3 font-semibold text-gray-900">{file.username}</td>
                        <td className="px-4 py-3 text-gray-600">{file.folder}</td>
                        <td className="px-4 py-3 text-gray-600">{file.filename}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            file.status === 'duplicate' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                          }`}>
                            {file.status === 'duplicate' ? 'Duplicate' : 'Unique'}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                            Kept
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* ZIP File 2 Details */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">
                ZIP File 2 - All Files ({summary.zip2_stats.total_files} files)
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Username</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Folder</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Filename</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Status</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {summary.zip2_stats.files.map((file, index) => (
                      <tr key={index} className={!file.kept ? 'bg-red-50 opacity-75' : 'hover:bg-gray-50'}>
                        <td className="px-4 py-3 font-semibold text-gray-900">{file.username}</td>
                        <td className="px-4 py-3 text-gray-600">{file.folder}</td>
                        <td className="px-4 py-3 text-gray-600">{file.filename}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            file.status === 'duplicate' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                          }`}>
                            {file.status === 'duplicate' ? 'Duplicate' : 'Unique'}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {file.kept ? (
                            <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                              Kept
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                              Removed
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Duplicate Pairs */}
            {summary.duplicate_pairs.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">
                  Duplicate Detection ({summary.duplicate_pairs.length} duplicates found)
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-4 py-3 text-left font-semibold text-gray-700">Username</th>
                        <th className="px-4 py-3 text-left font-semibold text-gray-700">ZIP 1 File</th>
                        <th className="px-4 py-3 text-left font-semibold text-gray-700">ZIP 2 File</th>
                        <th className="px-4 py-3 text-left font-semibold text-gray-700">Kept From</th>
                        <th className="px-4 py-3 text-left font-semibold text-gray-700">Removed From</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {summary.duplicate_pairs.map((pair, index) => (
                        <tr key={index} className="bg-yellow-50 hover:bg-yellow-100">
                          <td className="px-4 py-3 font-semibold text-gray-900">{pair.username}</td>
                          <td className="px-4 py-3">
                            <div className="text-gray-600">
                              <div className="text-xs text-gray-500 italic">{pair.zip1_file.folder}</div>
                              <div className="font-medium">{pair.zip1_file.filename}</div>
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <div className="text-gray-600">
                              <div className="text-xs text-gray-500 italic">{pair.zip2_file.folder}</div>
                              <div className="font-medium">{pair.zip2_file.filename}</div>
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                              {pair.kept_from}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                              {pair.removed_from}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Final Merged File List */}
            <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border-2 border-emerald-200 rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-2 mb-4">
                <DownloadIcon />
                <h3 className="text-xl font-bold text-gray-800">
                  Final Merged File List ({summary.final_merged.total_files} files)
                </h3>
              </div>
              <p className="text-sm text-gray-600 mb-4 italic">
                These files are included in the downloaded ZIP:
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm bg-white rounded-lg">
                  <thead className="bg-emerald-100">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Username</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Source</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Original Folder</th>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700">Original Filename</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {summary.final_merged.files.map((file, index) => (
                      <tr key={index} className="hover:bg-emerald-50">
                        <td className="px-4 py-3 font-semibold text-gray-900">{file.username}</td>
                        <td className="px-4 py-3 text-gray-600">{file.source}</td>
                        <td className="px-4 py-3 text-gray-600">{file.folder}</td>
                        <td className="px-4 py-3 text-gray-600">{file.filename}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
      </div>
              <div className="mt-4 p-3 bg-green-100 border border-green-300 rounded-lg">
                <p className="text-sm font-semibold text-green-800 flex items-center gap-2">
                  <CheckIcon />
                  The merged ZIP file has been automatically downloaded.
                </p>
              </div>
            </div>
          </div>
          )
        })()}

        {/* Info Section */}
        <div className="bg-white rounded-xl shadow-lg p-6 mt-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">How it works:</h2>
          <ul className="space-y-2 text-gray-600">
            <li className="flex items-start gap-2">
              <span className="text-blue-500 mt-1">•</span>
              <span>Upload two ZIP files containing PDF documents</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-500 mt-1">•</span>
              <span>The tool extracts usernames from PDF filenames (ZIP 1) and folder names (ZIP 2)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-500 mt-1">•</span>
              <span>PDFs are merged by username, removing duplicates</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-500 mt-1">•</span>
              <span>The final merged ZIP file is automatically downloaded</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default App
